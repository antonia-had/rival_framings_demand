import numpy as np
from matplotlib import pyplot as plt
plt.switch_backend('agg')
import pandas as pd
import argparse

plt.ioff()

def deliveries_scatter(sample, realization):
    fig_output_path = '../delivery_scatter_diff'
    months = 12
    years = 105
    ids_of_interest = np.genfromtxt('../ids.txt', dtype='str').tolist()

    fig, (ax1) = plt.subplots(1, 1, figsize=(14.5, 8))

    # Read data for state of the world
    df = pd.read_parquet(f'../xdd_parquet_flow/S{sample}_{realization}.parquet')

    for structure_id in ids_of_interest[:5]:
        '''
        Read and reshape flow experiment data
        '''
        mask = df['structure_id'] == structure_id
        new_df = df[mask]
        shortage_sow = (new_df['demand'].values - new_df['shortage'].values) * 1233.4818 / 1000000
        # Reshape data to a [no. years x no. months] matrix
        f_shortage_sow = np.reshape(shortage_sow, (years, months))
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

        shortage_adaptive = (df_demands['demand'].values - df_demands['shortage'].values) * 1233.4818 / 1000000

        # Reshape synthetic data
        # Reshape to matrix of [no. years x no. months x no. of rules]
        f_shortage_adaptive = np.reshape(shortage_adaptive, (total_number_rules, years, months))

        # Calculate all annual totals
        annual_totals = np.sum(f_shortage_adaptive, axis=2)

        for i in range(total_number_rules):
            ax1.scatter(f_shortage_sow_totals, annual_totals[i, :], marker='.', color='k', alpha=0.5)

    ax1.set_xlabel('Annual deliveries hydrologic scenario (Million $m^3$)', fontsize=18)
    ax1.set_ylabel('Annual deliveries under\nadaptive conditions (Million $m^3$)', fontsize=18)

    fig.suptitle(f'Delivery changes for S{sample}_{realization}', fontsize=18)
    plt.subplots_adjust(bottom=0.2)
    fig.savefig(f'{fig_output_path}/S{sample}_{realization}.png')
    fig.clf()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create distribution difference figure per ID')
    parser.add_argument('sample', type=str)
    parser.add_argument('realization', type=str)
    args = parser.parse_args()
    deliveries_scatter(args.sample, args.realization)