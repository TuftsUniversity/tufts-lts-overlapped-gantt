gnt.broken_barh(
    [(pd.to_datetime(start), pd.to_datetime(finish)-pd.to_datetime(start))],
    [int(df.loc[l, 'stack']), int(df.loc[l, 'level_of_effort'])],
    color=next(color),
    label=df.loc[l, 'task'])
