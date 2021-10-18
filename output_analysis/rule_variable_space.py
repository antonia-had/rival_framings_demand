import pandas as pd
import numpy as np
import argparse
from matplotlib import pyplot as plt
plt.switch_backend('agg')

plt.ioff()

def variable_effects(sample, realization, structure_id):
    fig_output_path = '../variable_effects'
    realization_years = 105
    months = 12

    '''
    Read flow experiment data
    '''
    # Read data for state of the world
    df = pd.read_parquet(f'../xdd_parquet_flow/S{sample}_{realization}.parquet')
    mask = df['structure_id'] == structure_id
    new_df = df[mask]
    deliveries_sow = (new_df['demand'].values - new_df['shortage'].values) * 1233.4818 / 1000000
    # Reshape data to a [no. years x no. months] matrix
    f_deliveries_sow = np.reshape(deliveries_sow, (realization_years, months))
    # Reshape to annual totals
    f_deliveries_sow_totals = np.sum(f_deliveries_sow, 1)
    # Value to compare to
    base_value = np.mean(f_deliveries_sow_totals)
    print(base_value)

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
                print(f'rule {r} applied to S{sample}_{realization} is missing')

    deliveries_adaptive = (df_demands['demand'].values - df_demands['shortage'].values) * 1233.4818 / 1000000

    # Reshape synthetic data
    # Reshape to matrix of [no. years x no. months x no. of rules]
    f_deliveries_adaptive = np.reshape(deliveries_adaptive, (total_number_rules, realization_years, months))

    # Calculate all annual totals
    annual_totals = np.sum(f_deliveries_adaptive, axis=2)

    print(len(annual_totals))

    # Create matrix to store annual total duration curves
    rule_value = base_value - np.mean(annual_totals, axis=1)

    rules_sample = np.loadtxt('../factorial_sample.txt', dtype=int)

    fig = plt.figure(1, 1, figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    im = ax.scatter(rules_sample[:, 0], rules_sample[:, 1], rules_sample[:, 2], c=rule_value, cmap='coolwarm', s=50)

    ax.set_xticks(list(np.arange(6)))
    ax.set_yticks(list(np.arange(10)))
    ax.set_zticks(list(np.arange(10)))

    ax.set_xticklabels(list(np.arange(75, 105, 5)))
    ax.set_yticklabels(list(np.arange(10, 110, 10)))
    ax.set_zticklabels(list(np.arange(10, 110, 10)))

    ax.set_xlabel('Historical flow percentile trigger')
    ax.set_ylabel('Rights included (% of total number)')
    ax.set_zlabel('Demand scaling level (% of total demand)')

    fig.colorbar(im, ax=ax, label='Difference in mean deliveries')

    fig.savefig(f'{fig_output_path}/S{sample}_{realization}_{structure_id}.png')
    fig.clf()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create distribution difference figure per ID')
    parser.add_argument('sample', type=str)
    parser.add_argument('realization', type=str)
    parser.add_argument('structure_id', type=str)
    args = parser.parse_args()
    variable_effects(args.sample, args.realization, args.structure_id)