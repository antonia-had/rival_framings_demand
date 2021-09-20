from statemod_data_extraction import create_file_per_structure_id
from mpi4py import MPI
import numpy as np
import math

structures = np.loadtxt('ids.txt')
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
    succesful_id = successful_structure_id(structures[k])
    if not succesful_id:
        print('Failed to create '+ structures[k])