from matplotlib.pyplot import cm

array = np.linspace(0, 1, len(df))
np.random.shuffle(array)
color = iter(cm.rainbow(array))
