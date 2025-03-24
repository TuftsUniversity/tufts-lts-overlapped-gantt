import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
from datetime import datetime
import numpy as np
from io import BytesIO
import textwrap
import mplcursors


def wrap_text(text, width=20):
    """Wraps the text to a specified width for labels."""
    return "\n".join(textwrap.wrap(text, width=width))


def generate_gantt_chart(jira_json):
    # Load the data from JSON
    projects_df = pd.DataFrame.from_dict(jira_json["data"], orient="index")

    # Default level_of_effort if all are null
    if projects_df['level_of_effort'].isnull().all():
        projects_df['level_of_effort'] = 2

    projects_df['level_of_effort'] = projects_df['level_of_effort'].astype("Int64")
    projects_df["stack"] = 0

    # Rename columns for consistency
    projects_df = projects_df.rename(columns={"Start date": "start_date", "Due date": "end_date"})
    projects_df = projects_df.dropna(subset=["start_date", "end_date"])

    # Clean and convert date columns
    projects_df["start_date"] = pd.to_datetime(projects_df["start_date"].astype(str).str.replace(" 00:00:00", ""))
    projects_df["end_date"] = pd.to_datetime(projects_df["end_date"].astype(str).str.replace(" 00:00:00", ""))

    # Sort for consistent stacking
    projects_df = projects_df.sort_values(["start_date", "end_date", "level_of_effort"])

    # Create the plotting matrix
    min_start_date = projects_df["start_date"].min()
    max_end_date = projects_df["end_date"].max()
    date_range = pd.date_range(start=min_start_date, end=max_end_date)
    height_of_matrix = max(int(projects_df["level_of_effort"].sum()), 7)

    # Integer-based index for stack levels
    stack_levels = list(reversed(range(height_of_matrix)))
    master_plotting_df = pd.DataFrame(0, index=stack_levels, columns=date_range)

    # Assign stack levels avoiding overlap
    for i, row in projects_df.iterrows():
        start = row["start_date"]
        end = row["end_date"]
        effort = int(row["level_of_effort"])
        date_slice = pd.date_range(start, end)

        for y in range(height_of_matrix - effort + 1):
            row_slice = list(range(y, y + effort))
            slice_df = master_plotting_df.loc[row_slice, date_slice]

            if (slice_df != 0).any().any():
                continue  # overlap, try next level
            else:
                # No conflict – assign and mark
                projects_df.at[i, "stack"] = y
                master_plotting_df.loc[row_slice, date_slice] = 1
                break

    # Plotting
    fig, gnt = plt.subplots(figsize=(16, 10))
    color_cycle = iter(cm.rainbow(np.linspace(0, 1, len(projects_df))))
    projects_df = projects_df.reset_index()

    for idx, row in projects_df.iterrows():
        start = row["start_date"]
        end = row["end_date"]
        duration = end - start
        stack = int(row["stack"])
        effort = int(row["level_of_effort"])
        status = row["Status"]
        title = wrap_text(row["Title"])
        next_color = next(color_cycle)

        # Define styling based on status
        if status == "Completed":
            color_value = next_color
            edgecolor = next_color
            hatch = ''
        elif status == "In Progress":
            color_value = "white"
            edgecolor = next_color
            hatch = '--'
        elif status == "Not Started":
            color_value = "white"
            edgecolor = next_color
            hatch = ''
        else:
            color_value = "black"
            edgecolor = "black"
            hatch = '--'

        # Draw bar
        gnt.broken_barh(
            [(start, duration)],
            [stack, effort],
            color=color_value,
            edgecolor=edgecolor,
            hatch=hatch,
            linewidth=3,
            label=title,
        )

        # Add centered label
        gnt.text(
            x=start + duration / 2,
            y=stack + effort / 2,
            s=title,
            ha="center",
            va="center",
            color="blue",
            fontsize="medium",
        )

    # Hover tooltips with mplcursors
    cursor = mplcursors.cursor(gnt.collections, hover=True)

    @cursor.connect("add")
    def on_hover(sel):
        index = sel.index
        sel.annotation.set_text(f"Next Steps: {projects_df.loc[index, 'Next Steps']}")
        sel.annotation.get_bbox_patch().set_boxstyle("round,pad=0.3")

    # Final layout
    gnt.set_xlabel("Date")
    gnt.set_ylabel("Rough Average Hours per Day\nEffort Level: Low=2, Medium=4, High=6")

    fig.tight_layout()
    plt.subplots_adjust(left=0.1, right=0.9, bottom=0.2, top=0.9)

    # Save as image in memory
    img = BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)

    return img
