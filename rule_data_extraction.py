import dask.dataframe as dd
from pathlib import Path
import argparse
from mpi4py import MPI


statemod_outputs = './xdd_parquet'
rule_outputs = './rules_parquet'

def create_file_per_rule(rule):
    df = dd.read_parquet(Path(f'{statemod_outputs}/**/S*_*_{rule}.parquet'),
                         engine='pyarrow-dataset').compute()
    df.to_parquet(Path(f'{rule_outputs}/{rule}.parquet'), engine='pyarrow',
                  compression='gzip')
    return True

# Begin parallel simulation
comm = MPI.COMM_WORLD

# Get the number of processors and the rank of processors
rank = comm.rank
nprocs = comm.size

# Divide all SOWs to available cores

# Determine the chunk which each processor will need to do
count = int(600/nprocs)
remainder = 600 % nprocs

# Use the processor rank to determine the chunk of work each processor will do
if rank < remainder:
    start = rank * (count+1)
    stop = start + count + 1
else:
    start = remainder * (count+1) + (rank-remainder) * count
    stop = start + count

print("Process " + str(rank) + " working on rules from " + str(start) + " to " + str(stop))
for k in range(start, stop):
    rule_success = create_file_per_rule(k)
    if not rule_outputs:
        print(f'Failed to create file for rule {k}')