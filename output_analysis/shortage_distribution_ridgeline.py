import numpy as np
from matplotlib import pyplot as plt
plt.switch_backend('agg')
import pandas as pd
import argparse
from scipy.stats.kde import gaussian_kde
from scipy.stats import norm

plt.ioff()

fig_output_path = '../distribution_diff_ridgeline'


def ridgeline(data, name, overlap=0, fill=True, labels=None, n_points=105):
    """
    Creates a standard ridgeline plot.
    Source: https://glowingpython.blogspot.com/2020/03/ridgeline-plots-in-pure-matplotlib.html
    data, list of lists.
    overlap, overlap between distributions. 1 max overlap, 0 no overlap.
    fill, matplotlib color to fill the distributions.
    n_points, number of points to evaluate each distribution function.
    labels, values to place on the y axis to describe the distributions.
    """
    if overlap > 1 or overlap < 0:
        raise ValueError('overlap must be in [0 1]')
    xx = np.linspace(np.min(np.concatenate(data)),
                     np.max(np.concatenate(data)), n_points)
    curves = []
    ys = []
    for i, d in enumerate(data):
        pdf = gaussian_kde(d)
        y = i*(1.0-overlap)
        ys.append(y)
        curve = pdf(xx)
        if fill:
            plt.fill_between(xx, np.ones(n_points)*y,
                             curve+y, zorder=len(data)-i+1, color=fill)
        plt.plot(xx, curve+y, c='k', zorder=len(data)-i+1)
    if labels:
        plt.yticks(ys, labels)
    plt.savefig(f'{fig_output_path}/{name}.pdf')

def read_data(sample, realization, structure_id):
    n = 12

    '''
    Read and reshape historical data
    '''
    # Read historical shortages for structure
    historical = pd.read_csv('../structures_files/shortages.csv', index_col=0)
    histData = historical.loc[structure_id].values * 1233.4818 / 1000000
    # Reshape historic data to a [no. years x no. months] matrix
    f_hist = np.reshape(histData, (int(np.size(histData) / n), n))
    # Reshape to annual totals
    f_hist_totals = np.sum(f_hist, 1)

    '''
    Read and reshape flow experiment data
    '''
    # Read data for state of the world
    df = pd.read_parquet(f'../xdd_parquet_flow/S{sample}_{realization}.parquet')
    mask = df['structure_id'] == structure_id
    new_df = df[mask]
    shortage_sow = new_df['shortage'].values * 1233.4818 / 1000000
    # Reshape data to a [no. years x no. months] matrix
    f_shortage_sow = np.reshape(shortage_sow, (int(np.size(histData) / n), n))
    # Reshape to annual totals
    f_shortage_sow_totals = np.sum(f_shortage_sow, 1)

    '''
    Read and reshape adaptive demand experiment data
    '''
    df_demands = pd.read_parquet(f'../temp_parquet/S{sample}_{realization}/S{sample}_{realization}_{structure_id}.parquet')
    # Check rules applied
    rules = df_demands['demand rule'].values
    applied_rules = np.unique(rules)
    total_number_rules = len(applied_rules)
    # Check rules applied
    if total_number_rules<600:
        # if rules are missing, check which
        for r in range(600):
            if r not in applied_rules:
                print(f'rule {n} applied to S{sample}_{realization} is missing')

    shortage_adaptive = df_demands['shortage'].values * 1233.4818 / 1000000

    # Reshape synthetic data
    # Reshape to matrix of [no. years x no. months x no. of rules]
    f_shortage_adaptive = np.reshape(shortage_adaptive, (total_number_rules, int(np.size(histData) / n), n))

    # Create matrix to store annual total duration curves
    F_syn = np.zeros([int(len(histData) / n), total_number_rules])

    # Calculate all annual totals
    annual_totals = np.sum(f_shortage_adaptive, axis=2)

    data = [list(f_hist_totals), list(f_shortage_sow_totals)].extend(annual_totals.tolist()[:10])
    return data

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create distribution difference figure per ID')
    parser.add_argument('sample', type=str)
    parser.add_argument('realization', type=str)
    parser.add_argument('structure_id', type=str)
    args = parser.parse_args()
    data = read_data(args.sample, args.realization, args.structure_id)
    print(np.shape(data))
    ridgeline(data, name=f'S{args.sample}_{args.realization}_{args.structure_id}',
              overlap=0.85, fill='yellow', labels=None, n_points=105)