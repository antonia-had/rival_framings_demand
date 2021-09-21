from mpi4py import MPI
import numpy as np
import math
import dask.dataframe as dd
from pathlib import Path
import logging

temporary_path = './xdd_parquet'
output_path = './parquet_outputs'

def create_file_per_structure_id(structure_id: str) -> bool:
	"""Reads a collection of parquet files and aggregates values for a structure_id into a single parquet file.

    Args:
        structure_id (str): the structure_id to aggregate

    Returns:
        bool: a boolean indicating whether aggregation was successful (True means success)
    """

	df = dd.read_parquet(
		Path(f'{temporary_path}/**/S*_*_*.parquet'),
		engine='pyarrow-dataset', filters=[['structure_id', '=', structure_id]]
	).compute()
	if len(df.index) == 0:
		logging.warning(f'No data for for structure_id: {structure_id}.')
		return False
	print("creating file for " + structure_id)
	df.to_parquet(
		Path(f'{output_path}/{structure_id}.parquet'),
		engine='pyarrow',
		compression='gzip'
	)
	return True

structures = np.genfromtxt('ids.txt', dtype='str').tolist()
total_number = len(structures)

# Begin parallel simulation
comm = MPI.COMM_WORLD

# Get the number of processors and the rank of processors
rank = comm.rank
nprocs = comm.size

# Determine the chunk which each processor will neeed to do
count = int(math.floor(total_number/nprocs))
remainder = total_number % nprocs

# Use the processor rank to determine the chunk of work each processor will do
if rank < remainder:
	start = rank*(count+1)
	stop = start + count + 1
else:
	start = remainder*(count+1) + (rank-remainder)*count
	stop = start + count

for k in range(start, stop):
    succesful_id = create_file_per_structure_id(structures[k])
    if not succesful_id:
        print('Failed to create '+ structures[k])