import pandas as pd
import plotly.express as pex
import matplotlib.pyplot as plt
from openpyxl import load_workbook
from datetime import datetime
from matplotlib.pyplot import cm
import numpy as np
import os
from io import BytesIO
import logging
import textwrap
import json
import matplotlib.patches as mpatches
from flask import send_file

from flask import Flask, request, jsonify, current_app


class ContinuousGantt:
    """Class to generate Gantt charts."""



    def wrap_text(self, text, width=20):
        """Wraps the text to a specified width."""
        return "\n".join(textwrap.wrap(text, width=width))
    # projects_df = pd.DataFrame.from_dict(jira_json["data"], orient="index")
    # with pd.option_context("display.max_columns", None):
    def __init__(self, jira_data):
        self.jira_data = jira_data



    def generate(self):
        jira_json = self.jira_data

        projects_df = pd.DataFrame.from_dict(jira_json["data"], orient="index")
        print(projects_df)
        # print(projects_df)
        # projects_df = jira_json.copy(0)
        # projects_df['level_of_effort'] = projects_df['level_of_effort'].astype("float")
        # projects_df['level_of_effort'] = projects_df['level_of_effort'].astype("Int64")

        projects_df = projects_df.reset_index()
        if projects_df.loc[0, "Parent Project"] != "":
            projects_df["level_of_effort"] = 1

        elif (
            projects_df["level_of_effort"].isnull().all()
            and projects_df["Parent Project"].isnull().all()
        ):
            projects_df["level_of_effort"] = 2

        projects_df["level_of_effort"] = projects_df["level_of_effort"].astype("Int64")
        projects_df["stack"] = 0
        # print(projects_df)
        projects_df = projects_df.sort_values(["Start date", "Due date", "level_of_effort"])
        projects_df = projects_df.rename(
            columns={"Start date": "start_date", "Due date": "end_date"}
        )
        pd.set_option("display.max_columns", None)
        pd.options.display.max_colwidth = 200

        projects_df = projects_df.dropna(subset=["start_date", "end_date"])
        projects_df["start_date"] = projects_df["start_date"].apply(
            lambda x: x.replace(" 00:00:00", "")
        )
        projects_df["end_date"] = projects_df["end_date"].apply(
            lambda x: x.replace(" 00:00:00", "")
        )

        min_start_date = (
            projects_df["start_date"]
            .apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))
            .min()
        )

        max_end_date = (
            projects_df["end_date"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d")).max()
        )

        delta = max_end_date - min_start_date
        length_of_matrix = delta

        delta = int(delta.total_seconds() / 60 / 60 / 24)
        height_of_matrix = int(projects_df["level_of_effort"].sum())
        if height_of_matrix < 7:
            height_of_matrix = 7
        rows, cols = (delta, height_of_matrix)
        arr = [[0] * cols] * rows

        date_range = pd.date_range(min_start_date, max_end_date)

        range_list = list(reversed(list(range(0, height_of_matrix))))

        for z in range(0, len(range_list)):
            range_list[z] = str(range_list[z])

        projects_df = projects_df.sort_values(
            ["start_date", "end_date", "level_of_effort"],
            ascending=[True, False, True],  # Specify the sorting order for each column
        )
        master_plotting_df = pd.DataFrame(
            data=np.zeros((height_of_matrix, len(date_range)), dtype=int),
            index=range(height_of_matrix),
            columns=date_range,
        )

        master_plotting_df = master_plotting_df.applymap(lambda x: 0)

        project_plotting_df = master_plotting_df.copy()

        # Assign stack levels avoiding overlap
        for i, row in projects_df.iterrows():
            start = row["start_date"]
            end = row["end_date"]
            effort = int(row["level_of_effort"])
            date_slice = pd.date_range(start, end)

            for y in range(height_of_matrix - effort + 1):
                row_slice = list(range(y, y + effort))  # keep as integers to match index
                try:
                    slice_df = master_plotting_df.loc[row_slice, date_slice]
                except KeyError as e:
                    logging.error(f"KeyError accessing plotting matrix at row {y}: {e}")
                    continue

                if (slice_df != 0).any().any():
                    continue  # overlap, try next level
                else:
                    # No conflict – assign and mark
                    projects_df.at[i, "stack"] = y
                    master_plotting_df.loc[row_slice, date_slice] = 1
                    break

        new_max_height_df = projects_df.copy()
        new_max_height = projects_df["stack"].max()
        new_max_height_df = projects_df[projects_df["stack"] == new_max_height]
        new_max_height_plus_level_of_effort = (
            int(new_max_height_df["level_of_effort"].max()) + new_max_height
        )

        df = projects_df.copy()
        df = df.reset_index()
        if df.loc[0, "Parent Project"] != "":
            unique_parents = df["Parent Project"].unique()
            parent_color_map = {
                parent: cm.rainbow(i / len(unique_parents))
                for i, parent in enumerate(unique_parents)
            }
            fig, gnt = plt.subplots(figsize=(12, 6))

            # array = np.linspace(0, 1, len(df))
            # np.random.shuffle(array)

            # color = iter(cm.rainbow(array))

            # df = df.reset_index()

            for l in range(0, len(df)):
                start = datetime.strptime(df.loc[l, "start_date"], "%Y-%m-%d")
                finish = datetime.strptime(df.loc[l, "end_date"], "%Y-%m-%d")
                status = df.loc[l, "Status"]
                parent_project = df.loc[l, "Parent Project"]
                parent_color = parent_color_map[parent_project]

                if status == "Completed":
                    color_value = parent_color
                    edgecolor = parent_color
                    hatch = ""
                elif status == "In Progress":
                    color_value = "white"
                    edgecolor = parent_color
                    hatch = "--"

                elif status == "Not Started":
                    color_value = "white"
                    edgecolor = parent_color
                    hatch = ""
                else:
                    color_value = "black"
                    edgecolor = "black"
                    hatch = "--"
                # Use the wrap_text function to wrap the Title field for the label
                gnt.broken_barh(
                    [
                        (
                            pd.to_datetime(start),
                            pd.to_datetime(finish) - pd.to_datetime(start),
                        )
                    ],
                    [int(df.loc[l, "stack"]), int(df.loc[l, "level_of_effort"])],
                    color=color_value,
                    edgecolor=edgecolor,
                    hatch=hatch,
                    linewidth=3,
                    label=self.wrap_text(df.loc[l, "Title"]),
                )
                # gnt.broken_barh(
                #     [(pd.to_datetime(start), pd.to_datetime(finish) - pd.to_datetime(start))],
                #     [int(df.loc[l, "stack"]), int(df.loc[l, "level_of_effort"])],
                #     color=next(color),
                #     label=df.loc[l, "Title"],
                # )

                data = [
                    (pd.to_datetime(start), pd.to_datetime(finish) - pd.to_datetime(start))
                ]

                title_number_map = {
                    title: str(i + 1) for i, title in enumerate(df["Title"].unique())
                }
                title_number = title_number_map[df.loc[l, "Title"]]
                for x1, x2 in data:
                    gnt.text(
                        x=x1 + x2 / 2,
                        y=(int(df.loc[l, "stack"]) + int(df.loc[l, "level_of_effort"]))
                        - int(df.loc[l, "level_of_effort"]) / 2,
                        s=title_number,
                        ha="center",
                        va="center",
                        color="blue",
                        fontsize=6,
                    )
            gnt.set_xlabel("Date")
            gnt.set_ylabel(
                "Rough Average Hours per Day\nEffort Level: Low=2, Medium=4, High= 6, Average for Project.  Most projects of any length are Low=2"
            )

            parent_legend_handles = [
                mpatches.Patch(color=color, label=self.wrap_text(parent, width=25))
                for parent, color in parent_color_map.items()
            ]
            parent_legend_handles = [
                mpatches.Patch(color=color, label=self.wrap_text(parent, width=25))
                for parent, color in parent_color_map.items()
            ]
            legend2 = gnt.legend(
                handles=parent_legend_handles,
                loc="lower left",
                bbox_to_anchor=(0.0, 0.0),
                title="Parent Projects",
                prop={"size": 6},
            )
            gnt.add_artist(legend2)

            # Title-number legend
            title_legend_handles = [
                mpatches.Patch(color="white", label=f"{num}: {self.wrap_text(title, width=40)}")
                for title, num in title_number_map.items()
            ]
            legend1 = gnt.legend(
                handles=title_legend_handles,
                loc="upper left",
                bbox_to_anchor=(1.02, 1.0),
                title="Project Titles",
                frameon=False,
                prop={"size": 6},
            )
            gnt.add_artist(legend1)
            # Shrink axis tick and label font sizes
            gnt.tick_params(axis="both", which="major", labelsize=6)
            gnt.xaxis.label.set_size(6)
            gnt.yaxis.label.set_size(6)
            # top_value_benchmark = 0.710 / 10
            # top_value = top_value_benchmark * new_max_height_plus_level_of_effort

            plt.subplots_adjust(left=0.1, right=0.85, bottom=0.15, top=0.9)
            # plt.xticks(rotation=45)
            # plt.show(block=True)
            # Generate the plot
            img = BytesIO()
            plt.savefig(img, format="png", dpi=100)

            img.seek(0)

            # (img, flush=True)
            return img

        else:
            fig, gnt = plt.subplots(figsize=(12, 6))  # half the height

            array = np.linspace(0, 1, len(df))
            np.random.shuffle(array)

            color = iter(cm.rainbow(array))

            # df = df.reset_index()

            for l in range(0, len(df)):
                start = datetime.strptime(df.loc[l, "start_date"], "%Y-%m-%d")
                finish = datetime.strptime(df.loc[l, "end_date"], "%Y-%m-%d")
                status = df.loc[l, "Status"]
                parent_project = df.loc[l, "Parent Project"]
                next_color = next(color)

                if status == "Completed":
                    color_value = next_color
                    edgecolor = next_color
                    hatch = ""
                elif status == "In Progress":
                    color_value = "white"
                    edgecolor = next_color
                    hatch = "--"

                elif status == "Not Started":
                    color_value = "white"
                    edgecolor = next_color
                    hatch = ""
                else:
                    color_value = "black"
                    edgecolor = "black"
                    hatch = "--"
                # Use the wrap_text function to wrap the Title field for the label
                gnt.broken_barh(
                    [
                        (
                            pd.to_datetime(start),
                            pd.to_datetime(finish) - pd.to_datetime(start),
                        )
                    ],
                    [int(df.loc[l, "stack"]), int(df.loc[l, "level_of_effort"])],
                    color=color_value,
                    edgecolor=edgecolor,
                    hatch=hatch,
                    linewidth=3,
                    label=self.wrap_text(df.loc[l, "Title"]),
                )
                # gnt.broken_barh(
                #     [(pd.to_datetime(start), pd.to_datetime(finish) - pd.to_datetime(start))],
                #     [int(df.loc[l, "stack"]), int(df.loc[l, "level_of_effort"])],
                #     color=next(color),
                #     label=df.loc[l, "Title"],
                # )

                data = [
                    (pd.to_datetime(start), pd.to_datetime(finish) - pd.to_datetime(start))
                ]

                for x1, x2 in data:
                    gnt.text(
                        x=x1 + x2 / 2,
                        y=(int(df.loc[l, "stack"]) + int(df.loc[l, "level_of_effort"]))
                        - int(df.loc[l, "level_of_effort"]) / 2,
                        s=self.wrap_text(df.loc[l, "Title"]),
                        ha="center",
                        va="center",
                        color="blue",
                        fontsize=6,
                    )
            gnt.set_xlabel("Date")
            gnt.set_ylabel(
                "Rough Average Hours per Day\nEffort Level: Low=2, Medium=4, High= 6, Average for Project.  Most projects of any length are Low=2"
            )

            # fig.legend(loc="upper left")

            # top_value_benchmark = 0.710 / 10
            # top_value = top_value_benchmark * new_max_height_plus_level_of_effort

            plt.subplots_adjust(left=0.1, right=0.9, bottom=0.2, top=0.9)
            # plt.xticks(rotation=45)
            # plt.show(block=True)
            # Generate the plot
            img = BytesIO()
            plt.savefig(img, format="png", dpi=100)

            img.seek(0)
           
            return img
            # (img, flush=True)
            # return img
        # plot_url = base64.b64encode(img.getvalue()).decode("utf8")

        # Use send_file to return the image for download
        # return send_file(img, mimetype='image/png', as_attachment=True, download_name='chart.png')
        # Create static/images directory if it doesn't exist
        # os.makedirs('static/images', exist_ok=True)

        # Save the file
        # plt.savefig('static/images/chart.png')

            