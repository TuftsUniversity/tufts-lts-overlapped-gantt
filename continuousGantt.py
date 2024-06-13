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


import pandas as pd
import plotly.express as pex
import matplotlib.pyplot as plt
from tkinter.filedialog import askopenfilename
import sys
import kaleido
from datetime import datetime
from datetime import date
from itertools import cycle
from matplotlib.pyplot import cm
import numpy as np
import re
#import plotly.graph_objects as go
filename = askopenfilename(title="Select project sheet")

#filename = "FY24 Projects DRAFT-v2.xlsx"

projects_df = pd.read_excel(filename, engine="openpyxl", dtype={'start_date': 'str', 'end_date': 'str', 'level_of_effort': 'Int64'})


projects_df = projects_df[['task', 'level_of_effort', 'start_date', 'end_date']].copy()
projects_df['stack'] = 0
projects_df = projects_df.sort_values(['start_date', 'end_date', 'level_of_effort'])
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
height_of_matrix = int(projects_df['level_of_effort'].sum())

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

# sys.exit()
project_plotting_df = master_plotting_df.copy()
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
            break


        else:
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

fig, gnt = plt.subplots(figsize=(16, 10))
array = np.linspace(0, 1, len(df))
np.random.shuffle(array)
color = iter(cm.rainbow(array))
#
# Plotting the area chart
# palette = cycle(pex.colors.qualitative.Bold)
# plt.style.use('ggplot')
for l in range(0, len(df)):
    #print(df.loc[l, 'start'])
    #print(df.loc[l, 'finish'])
    start = datetime.strptime(df.loc[l, 'start_date'], "%Y-%m-%d")
    #print(pd.to_datetime(start))
    #print(type(pd.to_datetime(start)))
    finish = datetime.strptime(df.loc[l, 'end_date'], "%Y-%m-%d")
    #print(type(pd.to_datetime(finish)))
    #print(type(pd.to_datetime(finish)))
    #gnt.broken_barh([(pd.to_datetime(start).timestamp(), pd.to_datetime(finish).timestamp()-pd.to_datetime(start).timestamp())], [int(df.loc[l, 'bandwidth']), int(df.loc[l, 'effort'])], color=next(color))
    gnt.broken_barh([(pd.to_datetime(start), pd.to_datetime(finish)-pd.to_datetime(start))], [int(df.loc[l, 'stack']), int(df.loc[l, 'level_of_effort'])], color=next(color), label=df.loc[l, 'task'])

    data = [(pd.to_datetime(start), pd.to_datetime(finish)-pd.to_datetime(start))]

    # print(data)
    for x1, x2 in data:
        gnt.text(x= x1 + x2/2,
                y= (int(df.loc[l, 'stack']) + int(df.loc[l, 'level_of_effort'])) - int(df.loc[l, 'level_of_effort'])/2,
                s=df.loc[l,  'task'],
                ha='center',
                va='center',
                color='blue',
                fontsize='xx-small',

               )

# ax.set_yticks(range(len(label)))
# ax.set_yticklabels(label)


# gantt = pex.timeline(df, x_start='start', x_end='finish',
#                      y='bandwidth', color='task', height=600, width=height)
# for i, d in enumerate(gantt.data):
#     gantt.data[i]['width'] = df.loc[x, 'width']
#
# fig.set_figheight(15)
# fig.set_figwidth(80)
# gnt.set_position([0, 0, 1, .6])
fig.tight_layout()
# fig.tight_layout()
gnt.set_xlabel("Date")
gnt.set_ylabel("Hours per Day")
#gnt.update_traces(marker_color=df.loc['task'].tolist(), marker_colorscale="Rainbow")
#gnt.set_ylabel('fruit supply')
#fig.show()
# gantt.update_traces(width=width_list)
#fig.write_image("yourfile.png")

fig.legend(ncol=3)

top_value_benchmark = .710/10

top_value = top_value_benchmark * new_max_height_plus_level_of_effort

plt.subplots_adjust(left=0.1, right=0.9, bottom=0.2, top=0.9)
figsize=(16, 10)
plt.xticks(rotation=45)
# plt.update_layout(legend=dict(font=dict(size(10))))
plt.show(block=True)
