import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
import holidays

# -----------------------------
# 1. Holiday generation helper
# -----------------------------
def get_holidays(year: int, country: str = "US") -> set:
    """
    Returns a set of holiday dates for a given year and country code (e.g., 'US', 'CA', 'UK').
    """
    try:
        country_holidays = holidays.country_holidays(country, years=[year])
        return set(country_holidays.keys())
    except Exception as e:
        print(f"Warning: could not load holidays for {country}. Defaulting to empty set. ({e})")
        return set()

# -----------------------------
# 2. Working day utilities
# -----------------------------
def working_days_between(start_d: date, end_d: date, holidays_set: set) -> int:
    """Count working days (Mon–Fri) between start and end, excluding holidays."""
    cur, cnt = start_d, 0
    while cur <= end_d:
        if cur.weekday() < 5 and cur not in holidays_set:
            cnt += 1
        cur += timedelta(days=1)
    return cnt

def split_spans_by_working_days(start_d: date, end_d: date, holidays_set: set):
    """Return (working_spans, nonworking_spans) for plotting as daily rectangles."""
    working_spans, nonworking_spans = [], []
    cur = start_d
    while cur <= end_d:
        start_dt = datetime.combine(cur, datetime.min.time())
        dur = timedelta(days=1)
        if cur.weekday() < 5 and cur not in holidays_set:
            working_spans.append((start_dt, dur))
        else:
            nonworking_spans.append((start_dt, dur))
        cur += timedelta(days=1)
    return working_spans, nonworking_spans

# -----------------------------
# 3. Main Gantt generator
# -----------------------------
def generate_stacked_gantt_with_holidays(projects_df, country="US"):
    """
    Draw a stacked Gantt chart:
    - Bars stack on the same line if their date ranges don’t overlap.
    - Working days are solid.
    - Weekends/holidays are hatched.
    """
    # --- compute holidays for all relevant years ---
    years = set(pd.to_datetime(projects_df["Start date"]).dt.year.tolist() +
                pd.to_datetime(projects_df["Due date"]).dt.year.tolist())
    holiday_set = set()
    for y in years:
        holiday_set |= get_holidays(y, country)

    # --- convert to date objects ---
    projects_df["state_date"] = pd.to_datetime(projects_df["Start date"]).dt.date
    projects_df["end_date"] = pd.to_datetime(projects_df["Due date"]).dt.date

    # --- compute working-day-based effort height ---
    projects_df["_working_days"] = projects_df.apply(
        lambda r: working_days_between(r["state_date"], r["end_date"], holiday_set), axis=1
    )
    projects_df["_effort_height"] = projects_df.apply(
        lambda r: (r["Story Points"] / r["_working_days"]) if r["_working_days"] > 0 else 0.0,
        axis=1
    )

    # --- end-to-end stacking: projects share a row if non-overlapping ---
    projects_df = projects_df.sort_values(by=["state_date"])
    stackend_dateates = []
    stacks = []
    for _, row in projects_df.iterrows():
        placed = False
        for i, end_date in enumerate(stackend_dateates):
            if row["state_date"] > end_date:
                stacks.append(i)
                stackend_dateates[i] = row["end_date"]
                placed = True
                break
        if not placed:
            stacks.append(len(stackend_dateates))
            stackend_dateates.append(row["end_date"])
    projects_df["stack"] = stacks

    # --- plotting ---
    fig, gnt = plt.subplots(figsize=(12, 6))
    for _, r in projects_df.iterrows():
        start_d, end_d = r["state_date"], r["end_date"]
        start_dt = datetime.combine(start_d, datetime.min.time())
        full_span = datetime.combine(end_d + timedelta(days=1), datetime.min.time()) - start_dt
        stack_y = int(r["stack"]) * 1.2
        height = r["_effort_height"]

        # Outline full calendar span
        gnt.broken_barh([(start_dt, full_span)], [stack_y, height],
                        facecolor="none", edgecolor="black", linewidth=1)

        # Split days into working/non-working
        working_spans, nonworking_spans = split_spans_by_working_days(start_d, end_d, holiday_set)
        if working_spans:
            gnt.broken_barh(working_spans, [stack_y, height], color="steelblue")
        if nonworking_spans:
            gnt.broken_barh(nonworking_spans, [stack_y, height],
                            facecolor="none", hatch="//", edgecolor="black")

        # Label project
        mid_x = start_dt + full_span / 2
        gnt.text(mid_x, stack_y + height / 2,
                 f'{r["Title"]}\n{int(r["Story Points"])} SP',
                 ha="center", va="center", fontsize=8, color="white", fontweight="bold")

    gnt.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    plt.xticks(rotation=45)
    gnt.set_xlabel("Calendar Days (Weekdays solid, Weekends/Holidays hatched)")
    gnt.set_ylabel("Effort Height = Story Points / Working Days")
    plt.title(f"Stacked Gantt Chart with Working-Day Hatching ({country})")
    plt.tight_layout()
    plt.show()
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
import holidays

# -----------------------------
# 1. Holiday generation helper
# -----------------------------
def get_holidays(year: int, country: str = "US") -> set:
    """
    Returns a set of holiday dates for a given year and country code (e.g., 'US', 'CA', 'UK').
    """
    try:
        country_holidays = holidays.country_holidays(country, years=[year])
        return set(country_holidays.keys())
    except Exception as e:
        print(f"Warning: could not load holidays for {country}. Defaulting to empty set. ({e})")
        return set()

# -----------------------------
# 2. Working day utilities
# -----------------------------
def working_days_between(start_d: date, end_d: date, holidays_set: set) -> int:
    """Count working days (Mon–Fri) between start and end, excluding holidays."""
    cur, cnt = start_d, 0
    while cur <= end_d:
        if cur.weekday() < 5 and cur not in holidays_set:
            cnt += 1
        cur += timedelta(days=1)
    return cnt

def split_spans_by_working_days(start_d: date, end_d: date, holidays_set: set):
    """Return (working_spans, nonworking_spans) for plotting as daily rectangles."""
    working_spans, nonworking_spans = [], []
    cur = start_d
    while cur <= end_d:
        start_dt = datetime.combine(cur, datetime.min.time())
        dur = timedelta(days=1)
        if cur.weekday() < 5 and cur not in holidays_set:
            working_spans.append((start_dt, dur))
        else:
            nonworking_spans.append((start_dt, dur))
        cur += timedelta(days=1)
    return working_spans, nonworking_spans

# -----------------------------
# 3. Main Gantt generator
# -----------------------------
def generate_stacked_gantt(projects_df, country="US"):
    """
    Backwards-compatible wrapper used by your Flask app.
    Delegates to the holiday-aware implementation.
    Returns a BytesIO PNG.
    """
    return generate_stacked_gantt_with_holidays(projects_df, country=country)


def generate_stacked_gantt_with_holidays(projects_df, country="US"):
    """
    Draw a stacked Gantt chart with weekend/holiday hatching and stacking.
    - If Parent Projects exist: color by parent and use Story Points / working days.
    - If Parent Projects are blank: use Level of Effort as height.
    - Working days are solid; weekends/holidays are hatched.
    - Returns BytesIO image for Flask.
    Columns expected: start_date, end_date, Title, Status, Parent Project (optional),
                      Story Points (child mode), level_of_effort (top-level mode).
    """
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import matplotlib.patches as mpatches
    from datetime import datetime, timedelta
    from io import BytesIO
    import numpy as np
    import textwrap
    import pandas as pd
    import holidays

    # ---------- helpers ----------
    def wrap_text(text, width=25):
        return "\n".join(textwrap.wrap(str(text), width=width))

    def get_holidays(year, country_code="US"):
        try:
            return set(holidays.country_holidays(country_code, years=[year]).keys())
        except Exception:
            return set()

    def working_days_between(start_d, end_d, holidays_set):
        cur, cnt = start_d, 0
        while cur <= end_d:
            if cur.weekday() < 5 and cur not in holidays_set:
                cnt += 1
            cur += timedelta(days=1)
        return cnt

    def split_spans_by_working_days(start_d, end_d, holidays_set):
        working_spans, nonworking_spans = [], []
        cur = start_d
        while cur <= end_d:
            start_dt = datetime.combine(cur, datetime.min.time())
            dur = timedelta(days=1)
            if cur.weekday() < 5 and cur not in holidays_set:
                working_spans.append((start_dt, dur))
            else:
                nonworking_spans.append((start_dt, dur))
            cur += timedelta(days=1)
        return working_spans, nonworking_spans

    # ---------- inputs & normalization ----------
    # make sure expected columns exist; fill safe defaults
    for col, default in [
        ("Title", ""),
        ("Status", "Unknown"),
        ("Parent Project", ""),
        ("Story Points", 0),
        ("level_of_effort", 0),
    ]:
        if col not in projects_df.columns:
            projects_df[col] = default

    # compute holidays for all relevant years
    years = set(pd.to_datetime(projects_df["start_date"]).dt.year.tolist()
                + pd.to_datetime(projects_df["end_date"]).dt.year.tolist())
    holiday_set = set()
    for y in years:
        holiday_set |= get_holidays(y, country)

    # convert to date objects (keep original keys!)
    projects_df["state_date"] = pd.to_datetime(projects_df["start_date"]).dt.date
    projects_df["end_date"]   = pd.to_datetime(projects_df["end_date"]).dt.date

    # determine mode: child/parent vs top-level only
    has_parents = projects_df["Parent Project"].notna().any() and (projects_df["Parent Project"].astype(str) != "").any()

    # compute bar height
    def compute_effort_height(row):
        wd = working_days_between(row["state_date"], row["end_date"], holiday_set)
        if wd == 0:
            return 0.0
        if has_parents and str(row.get("Parent Project", "")).strip() != "":
            # child items: SP / working_days
            return float(row.get("Story Points", 0)) / wd
        else:
            # top-level items: use LOE directly (already avg/day)
            return float(row.get("level_of_effort", 0))
    projects_df["_effort_height"] = projects_df.apply(compute_effort_height, axis=1)

    # ---------- end-to-end stacking (no overlap on same row) ----------
    projects_df = projects_df.sort_values(by=["state_date", "end_date"])
    stackend_dateates, stacks = [], []
    for _, row in projects_df.iterrows():
        placed = False
        for i, end_date in enumerate(stackend_dateates):
            if row["state_date"] > end_date:
                stacks.append(i)
                stackend_dateates[i] = row["end_date"]
                placed = True
                break
        if not placed:
            stacks.append(len(stackend_dateates))
            stackend_dateates.append(row["end_date"])
    projects_df["stack"] = stacks

    # ---------- plotting ----------
    fig, gnt = plt.subplots(figsize=(12, 6))

    if has_parents:
        # color map by Parent Project
        parent_vals = [p for p in projects_df["Parent Project"].unique() if str(p).strip() != ""]
        color_map = {p: plt.cm.rainbow(i / max(len(parent_vals), 1)) for i, p in enumerate(parent_vals)}

        for _, r in projects_df.iterrows():
            start_d, end_d = r["state_date"], r["end_date"]
            start_dt = datetime.combine(start_d, datetime.min.time())
            full_span = datetime.combine(end_d + timedelta(days=1), datetime.min.time()) - start_dt
            stack_y = int(r["stack"]) * 1.5
            height = max(float(r["_effort_height"]), 0.001)  # ensure visible bar

            parent_color = color_map.get(r.get("Parent Project", ""), "gray")
            status = str(r.get("Status", "Unknown"))

            # status-based styling
            if status == "Completed":
                fill_color, edgecolor = parent_color, parent_color
            elif status == "In Progress":
                fill_color, edgecolor = "white", parent_color
            elif status == "Not Started":
                fill_color, edgecolor = "white", parent_color
            else:
                fill_color, edgecolor = "black", "black"

            # outline full calendar span
            gnt.broken_barh([(start_dt, full_span)], [stack_y, height],
                            facecolor="none", edgecolor=edgecolor, linewidth=2)

            # daily slices for working/non-working
            working_spans, nonworking_spans = split_spans_by_working_days(start_d, end_d, holiday_set)
            if working_spans:
                gnt.broken_barh(working_spans, [stack_y, height], color=fill_color)
            if nonworking_spans:
                gnt.broken_barh(nonworking_spans, [stack_y, height],
                                facecolor="none", hatch="//", edgecolor=edgecolor)

            # label
            mid_x = start_dt + full_span / 2
            label_txt = f'{wrap_text(r["Title"], 25)}\n{int(r.get("Story Points", 0))} SP'
            gnt.text(mid_x, stack_y + height / 2, label_txt,
                     ha="center", va="center", fontsize=7, color="black")

        # legend for parents
        if parent_vals:
            patches = [mpatches.Patch(color=color_map[p], label=wrap_text(p, 25)) for p in parent_vals]
            gnt.legend(handles=patches, loc="upper right", fontsize=6, title="Parent Projects")

    else:
        # top-level only mode (LOE height, single palette)
        for _, r in projects_df.iterrows():
            start_d, end_d = r["state_date"], r["end_date"]
            start_dt = datetime.combine(start_d, datetime.min.time())
            full_span = datetime.combine(end_d + timedelta(days=1), datetime.min.time()) - start_dt
            stack_y = int(r["stack"]) * 1.5
            height = max(float(r["_effort_height"]), 0.001)

            status = str(r.get("Status", "Unknown"))
            if status == "Completed":
                fill_color, edgecolor = "steelblue", "steelblue"
            elif status == "In Progress":
                fill_color, edgecolor = "white", "steelblue"
            elif status == "Not Started":
                fill_color, edgecolor = "white", "gray"
            else:
                fill_color, edgecolor = "black", "black"

            gnt.broken_barh([(start_dt, full_span)], [stack_y, height],
                            facecolor="none", edgecolor=edgecolor, linewidth=2)

            working_spans, nonworking_spans = split_spans_by_working_days(start_d, end_d, holiday_set)
            if working_spans:
                gnt.broken_barh(working_spans, [stack_y, height], color=fill_color)
            if nonworking_spans:
                gnt.broken_barh(nonworking_spans, [stack_y, height],
                                facecolor="none", hatch="//", edgecolor=edgecolor)

            mid_x = start_dt + full_span / 2
            label_txt = f'{wrap_text(r["Title"], 25)}\nLOE {int(r.get("level_of_effort", 0))}'
            gnt.text(mid_x, stack_y + height / 2, label_txt,
                     ha="center", va="center", fontsize=7, color="black")

    # axes formatting
    gnt.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    gnt.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    plt.xticks(rotation=45)
    gnt.set_xlabel("Calendar Days (Weekdays solid, Weekends/Holidays hatched)")
    if has_parents:
        gnt.set_ylabel("Height = Story Points per Working Day")
    else:
        gnt.set_ylabel("Height = Level of Effort (avg hrs/day)")
    plt.title(f"Stacked Gantt with Working-Day Hatching ({country})")
    plt.tight_layout()

    # return image for Flask
    img = BytesIO()
    plt.savefig(img, format="png", dpi=110)
    img.seek(0)
    plt.close(fig)
    return img
