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

master_plotting_df = pd.DataFrame(columns=date_range, index=range_list)
master_plotting_df = master_plotting_df.applymap(lambda x: 0)

project_plotting_df = master_plotting_df.copy()
for x in range(0, len(projects_df)):
    
    y = 0
    while y + int(projects_df.iloc[x, projects_df.columns.get_loc('level_of_effort')]) < height_of_matrix:

        project_dates_and_effort_df = project_plotting_df.loc[str(y + int(projects_df.iloc[x, projects_df.columns.get_loc('level_of_effort')]) - 1): str(y), projects_df.iloc[x, projects_df.columns.get_loc('start_date')]: projects_df.iloc[x, projects_df.columns.get_loc('end_date')]]
        master_plotting_subslice_df = master_plotting_df.copy()


        if (project_dates_and_effort_df.equals(master_plotting_df.loc[str(y + int(projects_df.iloc[x, projects_df.columns.get_loc('level_of_effort')]) - 1): str(y), projects_df.iloc[x, projects_df.columns.get_loc('start_date')]: projects_df.iloc[x, projects_df.columns.get_loc('end_date')]])):
            projects_df.iloc[x, projects_df.columns.get_loc('stack')] = y
            #print("got in")
            master_plotting_df.loc[str(y + int(projects_df.iloc[x, projects_df.columns.get_loc('level_of_effort')]) - 1): str(y), projects_df.iloc[x, projects_df.columns.get_loc('start_date')]: projects_df.iloc[x, projects_df.columns.get_loc('end_date')]] =  master_plotting_df.loc[str(y + int(projects_df.iloc[x, projects_df.columns.get_loc('level_of_effort')]) - 1): str(y), projects_df.iloc[x, projects_df.columns.get_loc('start_date')]: projects_df.iloc[x, projects_df.columns.get_loc('end_date')]].applymap(lambda z: 1)


            y += 1
            break

        else:
            y += 1
