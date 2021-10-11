from mpi4py import MPI
import numpy as np
import math
import dask.dataframe as dd
from pathlib import Path
import logging

statemod_outputs = './xdd_parquet'
temporary_path = './temp_parquet'
output_path = './parquet_outputs'

def create_temporary_files_per_sow(sow: str) -> bool:
	"""Reads a collection of parquet files and aggregates values for a SOW and all IDs.

    Args:
    	sow (str): the SOW to aggregate
    Returns:
        bool: a boolean indicating whether aggregation was successful (True means success)
    """
	print("Read all files for " + sow)
	df = dd.read_parquet(
		Path(f'{statemod_outputs}/{sow}/S*_*_*.parquet'),
		engine='pyarrow-dataset').compute()
	for structure_id in structures:
		print("collecting all files for " + sow + ' ' + structure_id)
		new_df = df[(df.structure_id == structure_id)]
		if len(new_df.index) == 0:
			logging.warning(f'No data for for structure_id: {structure_id} in SOW {sow}.')
			return False
		print(f'Creating file {temporary_path}/{sow}_{structure_id}.parquet')
		new_df.to_parquet(
			Path(f'{temporary_path}/{sow}/{sow}_{structure_id}.parquet'),
			engine='pyarrow',
			compression='gzip'
		)
	return True

def create_file_per_structure_id(output_path, temporary_path, structure_id: str) -> bool:
	"""Reads a collection of parquet files and aggregates values for a structure_id into a single parquet file.

    Args:
        structure_id (str): the structure_id to aggregate

    Returns:
        bool: a boolean indicating whether aggregation was successful (True means success)
    """
	print("collecting all files for " + structure_id)
	df = dd.read_parquet(
		Path(f'{temporary_path}/**/S*_*_{structure_id}.parquet'),
		engine='pyarrow-dataset').compute()
	print("creating file for " + structure_id)
	df.to_parquet(
		Path(f'{output_path}/{structure_id}.parquet'),
		engine='pyarrow',
		compression='gzip'
	)
	return True

structures = np.genfromtxt('ids.txt', dtype='str').tolist()
total_number_structures = len(structures)

states_of_the_world = ['S'+str(i)+'_'+str(j) for i in range(1,101) for j in range (1,11)]
total_number_sows = len(states_of_the_world)

# Begin parallel simulation
comm = MPI.COMM_WORLD

# Get the number of processors and the rank of processors
rank = comm.rank
nprocs = comm.size

# # Divide all SOWs to available cores
#
# # Determine the chunk which each processor will need to do
# count = int(math.floor(total_number_sows/nprocs))
# remainder = total_number_sows % nprocs
#
# # Use the processor rank to determine the chunk of work each processor will do
# if rank < remainder:
# 	start = rank*(count+1)
# 	stop = start + count + 1
# else:
# 	start = remainder*(count+1) + (rank-remainder)*count
# 	stop = start + count
#
# print("Process " + str(rank) + " working on SOWs from " + str(start) + " to " + str(stop))
# for k in range(start, stop):
#     temporary_sow_id = create_temporary_files_per_sow(states_of_the_world[k])
#     if not temporary_sow_id:
#         print('Failed to create files for ' + states_of_the_world[k])

# comm.barrier()

# Divide all structure IDs to available cores

# Determine the chunk which each processor will need to do
count = int(math.floor(total_number_structures/nprocs))
remainder = total_number_structures % nprocs

# Use the processor rank to determine the chunk of work each processor will do
if rank < remainder:
	start = rank*(count+1)
	stop = start + count + 1
else:
	start = remainder*(count+1) + (rank-remainder)*count
	stop = start + count

print("Process " + str(rank) + " working on structures from " + str(start) + " to " + str(stop))

for s in range(start, stop):
    structure_output = create_file_per_structure_id(output_path, temporary_path, structures[s])
    if not structure_output:
        print('Failed to create file for ' + structures[s])

