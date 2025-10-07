import pandas as pd
import plotly.express as pex
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
import os
from io import BytesIO
import logging
import textwrap
import json
import matplotlib.patches as mpatches
import holidays

from flask import Flask, request, jsonify, current_app


def wrap_text(text, width=20):
    """Wraps the text to a specified width."""
    return "\n".join(textwrap.wrap(text, width=width))


def generate_gantt_chart(projects_df, country="US"):
    """
    Backwards-compatible wrapper used by your Flask app.
    Delegates to the holiday-aware implementation.
    Returns a BytesIO PNG.
    """
    return generate_stacked_gantt_with_holidays(projects_df, country=country)


def generate_stacked_gantt_with_holidays(projects_df, country="US"):
    """
    Draw a stacked Gantt chart with weekend/holiday hatching and stacking.
    - If Parent Projects exist: color by parent and use story_points / working days.
    - If Parent Projects are blank: use Level of Effort as height.
    - Working days are solid; weekends/holidays are hatched.
    - Returns BytesIO image for Flask.
    Columns expected: start_date, end_date, Title, Status, Parent Project (optional),
                      story_points (child mode), level_of_effort (top-level mode).
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

    def working_days_between(start_date, end_d, holidays_set):
        # Handle None, NaT, or invalid inputs gracefully
        if pd.isna(start_date) or pd.isna(end_d):
            return 0

        # Normalize types: convert pandas.Timestamp → datetime.date
        if isinstance(start_date, pd.Timestamp):
            start_date = start_date.to_pydatetime().date()
        if isinstance(end_d, pd.Timestamp):
            end_d = end_d.to_pydatetime().date()

        # If either is still not a date (e.g., string), skip
        if not isinstance(start_date, date) or not isinstance(end_d, date):
            return 0

        if end_d < start_date:
            return 0

        # Count working days excluding weekends and holidays
        cur, cnt = start_date, 0
        while cur <= end_d:
            if cur.weekday() < 5 and cur not in holidays_set:
                cnt += 1
            cur += timedelta(days=1)
        return cnt


    def split_spans_by_working_days(start_date, end_d, holidays_set):
        working_spans, nonworking_spans = [], []
        cur = start_date
        while cur <= end_d:
            start_date = datetime.combine(cur, datetime.min.time())
            dur = timedelta(days=1)
            if cur.weekday() < 5 and cur not in holidays_set:
                working_spans.append((start_date, dur))
            else:
                nonworking_spans.append((start_date, dur))
            cur += timedelta(days=1)
        return working_spans, nonworking_spans

    # ---------- inputs & normalization ----------
    # make sure expected columns exist; fill safe defaults
    
    projects_df = pd.DataFrame.from_dict(projects_df["data"], orient="index").reset_index(drop=True)

    print(projects_df)

    # Normalize and clean date columns early
    projects_df["start_date"] = pd.to_datetime(projects_df["start_date"], errors="coerce")
    projects_df["end_date"]   = pd.to_datetime(projects_df["end_date"], errors="coerce")


    # compute holidays for all relevant years
    years = set(pd.to_datetime(projects_df["start_date"]).dt.year.tolist()
                + pd.to_datetime(projects_df["end_date"]).dt.year.tolist())
    holiday_set = set()
    for y in years:
        holiday_set |= get_holidays(y, country)

    # convert to date objects (keep original keys!)
    projects_df["start_date"] = pd.to_datetime(projects_df["start_date"]).dt.date
    projects_df["end_date"]   = pd.to_datetime(projects_df["end_date"]).dt.date

    # determine mode: child/parent vs top-level only
    has_parents = projects_df["Parent Project"].notna().any() and (projects_df["Parent Project"].astype(str) != "").any()

    # compute bar height
    def compute_effort_height(row):
        wd = working_days_between(row["start_date"], row["end_date"], holiday_set)
        if wd == 0:
            return 0.0

        # Safely convert story_points and level_of_effort to float
        def safe_float(v):
            try:
                return float(v) if str(v).strip() != "" else 0.0
            except Exception:
                return 0.0

        if has_parents and str(row.get("Parent Project", "")).strip() != "":
            return safe_float(row.get("story_points", 0)) / wd
        else:
            return safe_float(row.get("level_of_effort", 0))
    projects_df["effort_height"] = projects_df.apply(compute_effort_height, axis=1)

   # ---------- end-to-end stacking (no overlap on same row) ----------
    projects_df = projects_df.dropna(subset=["start_date", "end_date"]).copy()
    projects_df = projects_df.sort_values(by=["start_date", "end_date"])

    stack_end_dates = []  # track the latest end date per stack
    stacks = []           # the assigned stack index per task


    for _, row in projects_df.iterrows():
        start = pd.to_datetime(row["start_date"])
        end = pd.to_datetime(row["end_date"])

        placed = False
        for i, end_date in enumerate(stack_end_dates):
            # if this task starts AFTER a previous one ends, reuse that lane
            if pd.notna(end_date) and start > end_date:
                stacks.append(i)
                stack_end_dates[i] = end
                placed = True
                break

        if not placed:
            stacks.append(len(stack_end_dates))
            stack_end_dates.append(end)

    projects_df["stack"] = stacks


    # pd.set_option('display.max_columns', None)  # or 1000
    # pd.set_option('display.max_rows', None)  # or 1000
    # print(projects_df)    
    # ---------- plotting ----------
    fig, gnt = plt.subplots(figsize=(12, 6))

    if has_parents:
        # color map by Parent Project
        parent_vals = [p for p in projects_df["Parent Project"].unique() if str(p).strip() != ""]
        color_map = {p: plt.cm.rainbow(i / max(len(parent_vals), 1)) for i, p in enumerate(parent_vals)}
        projects_df = projects_df.dropna(subset=["story_points"])
        projects_df["story_points"] = projects_df["story_points"].astype(int)

        print("\n\n\n\n\n\n")
        print(projects_df)
        legend_labels = []  # NEW: holds (number, title)

        
        # --- track unique tasks for numbering ---
        task_number_map = {}
        legend_labels = []
        task_counter = 1

        for idx, r in projects_df.iterrows():
            start_date, end_d = r["start_date"], r["end_date"]
            start_date = datetime.combine(start_date, datetime.min.time())
            full_span = datetime.combine(end_d + timedelta(days=1), datetime.min.time()) - start_date
            stack_y = int(r["stack"]) * 1.5
            height = max(float(r["effort_height"]), 0.001)  # ensure visible bar

            parent_color = color_map.get(r.get("Parent Project", ""), "gray")
            status = str(r.get("Status", "Unknown"))

            # --- assign one legend number per unique task ---
            task_key = (r["Title"], r.get("Parent Project", ""))
            if task_key not in task_number_map:
                task_number_map[task_key] = task_counter
                legend_labels.append((task_counter, r["Title"]))
                task_counter += 1
            task_num = task_number_map[task_key]

            # --- status-based styling ---
            if status == "Completed":
                fill_color, edgecolor = parent_color, parent_color
            elif status == "In Progress":
                fill_color, edgecolor = "white", parent_color
            elif status == "Not Started":
                fill_color, edgecolor = "white", parent_color
            else:
                fill_color, edgecolor = "black", "black"

            # --- outline full calendar span ---
            gnt.broken_barh([(start_date, full_span)], [stack_y, height],
                            facecolor="none", edgecolor=edgecolor, linewidth=2)

            # --- daily slices for working/non-working ---
            working_spans, nonworking_spans = split_spans_by_working_days(
                r["start_date"], r["end_date"], holiday_set
            )

            if working_spans:
                gnt.broken_barh(working_spans, [stack_y, height], color=fill_color)
            if nonworking_spans:
                gnt.broken_barh(nonworking_spans, [stack_y, height],
                                facecolor="none", hatch="//", edgecolor=edgecolor)

            # --- label: show number only (story points in legend already) ---
            mid_x = start_date + full_span / 2
            gnt.text(
                mid_x, stack_y + height / 2, str(task_num),
                ha="center", va="center", fontsize=8,
                color="black", fontweight="bold"
            )

        # --- legend for parent projects (existing behavior) ---
        if parent_vals:
            patches = [mpatches.Patch(color=color_map[p], label=wrap_text(p, 25)) for p in parent_vals]
            gnt.legend(handles=patches, loc="upper right", fontsize=6, title="Parent Projects")

        # --- two-column task legend at top-left ---
        if legend_labels:
            # split legend roughly in half
            mid = (len(legend_labels) + 1) // 2
            col1 = legend_labels[:mid]
            col2 = legend_labels[mid:]

            col1_text = "\n".join([f"{num}: {wrap_text(title, 45)}" for num, title in col1])
            col2_text = "\n".join([f"{num}: {wrap_text(title, 45)}" for num, title in col2])

            # adjust plot to make space for legend text
            box = gnt.get_position()
            gnt.set_position([box.x0, box.y0, box.width, box.height * 0.8])

            fig = plt.gcf()
            fig.text(
                0.02, 0.98, col1_text,
                fontsize=7, va="top", ha="left", wrap=True, transform=fig.transFigure,
            )
            fig.text(
                0.30, 0.98, col2_text,
                fontsize=7, va="top", ha="left", wrap=True, transform=fig.transFigure,
            )


    else:
        # top-level only mode (LOE height, single palette)
        for _, r in projects_df.iterrows():
            start_date, end_d = r["start_date"], r["end_date"]
            start_date = datetime.combine(start_date, datetime.min.time())
            full_span = datetime.combine(end_d + timedelta(days=1), datetime.min.time()) - start_date
            stack_y = int(r["stack"]) * 1.5
            height = max(float(r["effort_height"]), 0.001)

            status = str(r.get("Status", "Unknown"))
            if status == "Completed":
                fill_color, edgecolor = "steelblue", "steelblue"
            elif status == "In Progress":
                fill_color, edgecolor = "white", "steelblue"
            elif status == "Not Started":
                fill_color, edgecolor = "white", "gray"
            else:
                fill_color, edgecolor = "black", "black"

            gnt.broken_barh([(start_date, full_span)], [stack_y, height],
                            facecolor="none", edgecolor=edgecolor, linewidth=2)

            working_spans, nonworking_spans = split_spans_by_working_days(r["start_date"], r["end_date"], holiday_set)

            if working_spans:
                gnt.broken_barh(working_spans, [stack_y, height], color=fill_color)
            if nonworking_spans:
                gnt.broken_barh(nonworking_spans, [stack_y, height],
                                facecolor="none", hatch="//", edgecolor=edgecolor)

            mid_x = start_date + full_span / 2
            label_txt = f'{wrap_text(r["Title"], 25)}\nLOE {int(r.get("level_of_effort", 0))}'
            gnt.text(mid_x, stack_y + height / 2, label_txt,
                     ha="center", va="center", fontsize=7, color="black")

    # axes formatting
    # --- X-axis: show one tick per week (Monday start) ---
    gnt.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=1))
    gnt.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))

    plt.xticks(rotation=45)
    gnt.set_xlabel("Calendar Days (Weekdays solid, Weekends/Holidays hatched)")
    if has_parents:
        gnt.set_ylabel("Height = story_points per Working Day")
    else:
        gnt.set_ylabel("Height = Level of Effort (avg hrs/day)")
    plt.title(f"Stacked Gantt with Working-Day Hatching ({country})")
    # Fix x-axis scaling to the earliest and latest project dates
    # Fix x-axis scaling safely, even if some rows have NaT/NaN dates
    valid_dates = projects_df.dropna(subset=["start_date", "end_date"]).copy()
    if not valid_dates.empty:
        min_date = pd.to_datetime(valid_dates["start_date"]).min().date()
        max_date = pd.to_datetime(valid_dates["end_date"]).max().date() + timedelta(days=1)
        gnt.set_xlim(datetime.combine(min_date, datetime.min.time()),
                    datetime.combine(max_date, datetime.min.time()))

    plt.tight_layout()

    # return image for Flask
    img = BytesIO()
    plt.savefig(img, format="png", dpi=110)
    img.seek(0)
    plt.close(fig)
    return img
