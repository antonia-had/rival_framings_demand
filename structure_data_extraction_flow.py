import argparse
import dask.dataframe as dd
from pathlib import Path


def create_file_per_structure_id(output_path, temporary_path, structure_id: str) -> bool:
	"""Reads a collection of parquet files and aggregates values for a structure_id into a single parquet file.

    Args:
        structure_id (str): the structure_id to aggregate

    Returns:
        bool: a boolean indicating whether aggregation was successful (True means success)
    """
	print("collecting all files for " + structure_id)
	df = dd.read_parquet(
		Path(f'{temporary_path}/S*_*.parquet'),
		engine='pyarrow-dataset').compute()
	print("creating file for " + structure_id)
	df.to_parquet(
		Path(f'{output_path}/{structure_id}.parquet'),
		engine='pyarrow',
		compression='gzip'
	)
	return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create .parquet per ID')
    parser.add_argument('output_path', type=str)
    parser.add_argument('temporary_path', type=str,
                        help='path to .parquet files')
    parser.add_argument('structure_id', type=str)
    args = parser.parse_args()
    create_file_per_structure_id(args.output_path, args.temporary_path, args.structure_id)