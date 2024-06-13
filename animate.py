import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tkinter.filedialog import askopenfilename
from datetime import datetime, timedelta
from itertools import cycle
from matplotlib.animation import FuncAnimation

import sys
import kaleido
from datetime import datetime
from datetime import date
from itertools import cycle
from matplotlib.pyplot import cm

import re
# import pandas as pd
# import plotly.express as pex
#
# d1 = dict(stack=1, start='2023-09-01', finish='2023-10-01', task='Sleep')
# d2 = dict(stack=1, start='2023-10-01', finish='2021-10-15', task='EAT')
# d3 = dict(stack=1, start='2023-09-15', finish='2023-09-30', task='Study')
# d4 = dict(stack=1, start='2023-10-10', finish='2023-10-30', task='Work')
# d5 = dict(stack=1, start='2023-10-15', finish='2023-10-30', task='EAT')
# d6 = dict(stack=1, start='2023-10-15', finish='2023-11-01', task='Study')
# d8 = dict(stack=1, start='2023-11-02', finish='2023-11-15', task='EAT')
# d7 = dict(stack=1, start='2023-11-02', finish='2023-11-15', task='Sleep')
#
# dict_list = [d1,d2,d3,d4,d5,d6,d7,d8]
# for dict in dict_list:
#
#
#
# df = pd.DataFrame([d1,d2,d3,d4,d5,d6,d7,d8])
#
# gantt = pex.timeline(df, x_start='start', x_end='finish', y='stack', color='task', height=300)
# gantt



#import plotly.graph_objects as go
filename = askopenfilename(title="Select project sheet")

#filename = "FY24 Projects DRAFT-v2.xlsx"

projects_df = pd.read_excel(filename, engine="openpyxl", dtype={'start_date': 'str', 'end_date': 'str'})

projects_df['stack'] = 0
projects_df = projects_df.sort_values(['start_date', 'end_date'])
pd.set_option('display.max_columns', None)
pd.options.display.max_colwidth = 200
print(projects_df)



# projects_df['start_date'] = projects_df['start_date'].apply(lambda x: re.sub(r'(\d{4}-\d{2}-\d{2}).*$', r'\1', x))
# projects_df['end_date'] = projects_df['end_date'].apply(lambda x: re.sub(r'(\d{4}-\d{2}-\d{2}).*$', r'\1', x))



min_start_date = projects_df['start_date'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d")).min()

max_end_date = projects_df['end_date'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d")).max()#  max_end_date = projects_df.max(pd.to_datetime('finish'))
delta = max_end_date - min_start_date
length_of_matrix = delta

delta = int(delta.total_seconds()/60/60/24)
height_of_matrix = projects_df['level_of_effort'].sum()

print("Height of matrix: " + str(height_of_matrix))

print("Width of Matrix:  " + str(delta))
rows, cols = (delta, height_of_matrix)
arr = [[0]*cols]*rows

date_range = pd.date_range(min_start_date, max_end_date)

range_list = list(reversed(list(range(0, height_of_matrix))))

for z in range(0, len(range_list)):

    range_list[z] = str(range_list[z])
    # print (range_list[z])
    # print(type(range_list[z]))



master_plotting_df = pd.DataFrame(columns=date_range, index=range_list)

master_plotting_df = master_plotting_df.applymap(lambda x: 0)


# print(master_plotting_df)
animation_frames = []
# sys.exit()
project_plotting_df = master_plotting_df.copy()
for x in range(0, len(projects_df)):
    # if x == 4:
    #     break



    # print(project_plotting_df)


    #print(str(x) + " time through")
    y = 0
    while y + int(projects_df.iloc[x, projects_df.columns.get_loc('level_of_effort')]) < height_of_matrix:

        #print(str(y + int(projects_df.loc[x, 'level_of_effort']) - 1))

        #try:
        project_dates_and_effort_df = project_plotting_df.loc[str(y + int(projects_df.iloc[x, projects_df.columns.get_loc('level_of_effort')]) - 1): str(y), projects_df.iloc[x, projects_df.columns.get_loc('start_date')]: projects_df.iloc[x, projects_df.columns.get_loc('end_date')]]

        #except:
        #    break
        master_plotting_subslice_df = master_plotting_df.copy()

        #master_plotting_subslice_df = master_plotting_df.loc[str(y + int(projects_df.iloc[x, projects_df.columns.get_loc('level_of_effort')]) - 1): str(y), projects_df.loc[x, 'start_date']: projects_df.loc[x, 'end_date']].loc[str(y + int(projects_df.iloc[x, projects_df.columns.get_loc('level_of_effort')]) - 1): str(y), projects_df.loc[x, 'start_date']: projects_df.loc[x, 'end_date']]





        # print(project_dates_and_effort_df.equals(master_plotting_subslice_df))
        # sys.exit()



        if (project_dates_and_effort_df.equals(master_plotting_df.loc[str(y + int(projects_df.iloc[x, projects_df.columns.get_loc('level_of_effort')]) - 1): str(y), projects_df.iloc[x, projects_df.columns.get_loc('start_date')]: projects_df.iloc[x, projects_df.columns.get_loc('end_date')]])):
            projects_df.iloc[x, projects_df.columns.get_loc('stack')] = y
            #print("got in")
            master_plotting_df.loc[str(y + int(projects_df.iloc[x, projects_df.columns.get_loc('level_of_effort')]) - 1): str(y), projects_df.iloc[x, projects_df.columns.get_loc('start_date')]: projects_df.iloc[x, projects_df.columns.get_loc('end_date')]] =  master_plotting_df.loc[str(y + int(projects_df.iloc[x, projects_df.columns.get_loc('level_of_effort')]) - 1): str(y), projects_df.iloc[x, projects_df.columns.get_loc('start_date')]: projects_df.iloc[x, projects_df.columns.get_loc('end_date')]].applymap(lambda z: 1)



            # if x == 1:

            #     print(master_plotting_df.loc[str(y + int(projects_df.iloc[x, projects_df.columns.get_loc('level_of_effort')]) - 1): str(y), projects_df.iloc[x, projects_df.columns.get_loc('start_date')]: projects_df.iloc[x, projects_df.columns.get_loc('end_date')]])
            #     print(project_dates_and_effort_df)
            #     sys.exit()
            #print(master_plotting_df.loc[str(y + int(projects_df.iloc[x, projects_df.columns.get_loc('level_of_effort')]) - 1): str(y), projects_df.loc[x, 'start_date']: projects_df.loc[x, 'end_date']])



            #master_plotting_df.to_excel("Plotting Dataframe for Testing - " +str(x) + ".xlsx")
            y += 1
            animation_frames.append(projects_df.copy())
            break


        else:
            animation_frames.append(projects_df.copy())
            y += 1
            #print('miss')

#master_plotting_df.to_excel("Plotting DataFrame.xlsx")
print(projects_df)

new_max_height_df = projects_df.copy()

new_max_height = projects_df['stack'].max()

new_max_height_df = projects_df[projects_df['stack'] == new_max_height]

new_max_height_plus_level_of_effort = int(new_max_height_df['level_of_effort'].max()) + new_max_height
# print(new_max_height_df)
# print(new_max_height_plus_level_of_effort)




df = projects_df.copy()

# Set up the figure and axis for animation
fig, gnt = plt.subplots(figsize=(16, 10))
array = np.linspace(0, 1, len(df))
np.random.shuffle(array)
colors = cycle(iter(cm.rainbow(array)))
# Function to update the plot using animation_frames
def update_plot(i):
    gnt.cla()  # Clear the axis
    current_frame = animation_frames[i]

    for index, row in projects_df.iterrows():
        try:
            start_date = datetime.strptime(row['start_date'], "%Y-%m-%d")
            end_date = datetime.strptime(row['end_date'], "%Y-%m-%d")
            duration = (end_date - start_date).days
            stack = int(current_frame.loc[index, 'stack'])
            level_of_effort = int(current_frame.loc[index, 'level_of_effort'])
            task = current_frame.loc[index, 'task']
            color = next(colors)

            gnt.broken_barh([(pd.to_datetime(start_date), pd.to_datetime(end_date)-pd.to_datetime(start_date))], [int(current_frame.loc[index, 'stack']), int(current_frame.loc[index, 'level_of_effort'])], color=color, label=current_frame.loc[index, 'task'])


            gnt.text(
                x=start_date + timedelta(days=duration / 2),
                y=(stack + level_of_effort) - level_of_effort / 2,
                s=task,
                ha='center',
                va='center',
                color='blue',
                fontsize='xx-small'
            )
        except Exception as e:
            print(e)
    gnt.set_xlabel('Time')
    gnt.set_ylabel('Task Effort')
    gnt.set_title('Animated Broken Barh Plot')

# Create the animation
ani = FuncAnimation(fig, update_plot, frames=len(animation_frames), repeat=False)

# Display the animation
plt.show()
