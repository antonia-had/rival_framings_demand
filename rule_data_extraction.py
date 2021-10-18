import dask.dataframe as dd
from pathlib import Path
import argparse

statemod_outputs = './xdd_parquet'
rule_outputs = './rules_parquet'

def create_file_per_rule(rule):
    df = dd.read_parquet(Path(f'{statemod_outputs}/**/S*_*_{rule}.parquet'),
                         engine='pyarrow-dataset').compute()
    df.to_parquet(Path(f'{rule_outputs}/{rule}.parquet'), engine='pyarrow',
                  compression='gzip')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create summary parquet per rule')
    parser.add_argument('rule', type=str)
    args = parser.parse_args()
    create_file_per_rule(args.rule)