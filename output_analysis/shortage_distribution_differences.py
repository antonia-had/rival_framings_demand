import numpy as np
from matplotlib import pyplot as plt
plt.switch_backend('agg')
from scipy import stats
import pandas as pd
import argparse

plt.ioff()

def plotSDC(sample, realization, structure_id):
    fig_output_path = '../distribution_diff'
    percentiles = np.arange(0, 100)
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
    # Calculate historical shortage duration curves
    F_hist = np.sort(f_hist_totals)  # for inverse sorting add this at the end [::-1]

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
    # Calculate shortage duration curves
    F_sow_shortages = np.sort(f_shortage_sow_totals)  # for inverse sorting add this at the end [::-1]

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
    f_shortage_adaptive = np.reshape(shortage_adaptive, (int(np.size(histData) / n), n, total_number_rules))

    # Create matrix to store annual total duration curves
    F_syn = np.zeros([int(len(histData) / n), total_number_rules])

    # Calculate all annual totals
    annual_totals = np.sum(f_shortage_adaptive, axis=1)

    # Calculate synthetic shortage duration curves
    # Loop through every SOW and sort
    for j in range(total_number_rules):
        F_syn[:, j] = np.sort(annual_totals[:, j])

    p = np.arange(100, -10, -50)

    P = np.arange(1., len(histData)/12 + 1) * 100 / (len(histData)/12)

    ylimit = max(np.max(F_syn), np.max(F_hist), np.max(F_sow_shortages))

    fig, (ax1) = plt.subplots(1, 1, figsize=(14.5, 8))
    # ax1
    handles = []
    labels = []
    colors = ['#000292', '#BB4430']
    ax1.fill_between(P, y1=np.amin(F_syn, axis=1),
                     y2=np.amax(F_syn, axis=1), color=colors[0], alpha=0.5)
    ax1.plot(P, F_sow_shortages, c=colors[0], linewidth=2, label='SOW without adaptive demands')
    ax1.plot(P, F_hist, c='black', linewidth=2, label='Historical record')
    ax1.set_ylim(0, ylimit)
    ax1.set_xlim(0, 100)
    ax1.legend(handles=handles, labels=labels, framealpha=1, fontsize=8, loc='upper left',
               title='Frequency in experiment', ncol=2)
    ax1.set_xlabel('Shortage magnitude percentile', fontsize=20)
    ax1.set_ylabel('Annual shortage (Million $m^3$)', fontsize=20)

    fig.suptitle('Shortage magnitudes for ' + structure_id, fontsize=16)
    plt.subplots_adjust(bottom=0.2)
    #fig.savefig(fig_output_path + '/' + structure_id + '.svg')
    fig.savefig(fig_output_path + '/' + structure_id + '.png')
    fig.clf()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create distribution difference figure per ID')
    parser.add_argument('sample', type=str)
    parser.add_argument('realization', type=str)
    parser.add_argument('structure_id', type=str)
    args = parser.parse_args()
    plotSDC(args.sample, args.realization, args.structure_id)