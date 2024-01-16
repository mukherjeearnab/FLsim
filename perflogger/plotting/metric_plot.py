import matplotlib.pyplot as plt
# import seaborn as sns
# import numpy as np
import datetime
import pandas as pd


def load_plot(projects, metric: str):
    for project in projects:
        x, y = load_series(project, metric)

        plt.plot(x, y, label=project)

    plt.legend(loc="lower right")

    plot_name = '{date:%Y-%m-%d_%H:%M:%S}'.format(
        date=datetime.datetime.now())
    plt.savefig(f'./plots/{plot_name}.png')


def load_series(project, metric='accuracy'):
    data = pd.read_csv(f'./projects/{project}/perflog.csv')
    data = data[data['node'] == 'server']

    return data['round'], data[metric]


def main():
    projects = [
        'c-fedavg-10-2023-12-26_13:06:53',
        'c-moon-10-2023-12-26_15:16:02',
        'gcon-4-2023-12-24_10:44:47',
        'fedprox-bench2-2023-12-13_06:42:19'
    ]

    load_plot(projects, 'accuracy')


main()
