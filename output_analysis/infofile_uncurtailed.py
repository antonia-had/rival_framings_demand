from mpi4py import MPI
import math
import numpy as np
import os
import sys
import glob
from getinfo import getinfo

# =============================================================================
# Experiment set up
# =============================================================================
comm = MPI.COMM_WORLD
# Get the number of processors and the rank of processors
rank = comm.rank
nprocs = comm.size

design = str(sys.argv[1])

# Read in SOW parameters
os.chdir('../' + design)
directories = glob.glob('CMIP*_*')
os.chdir('../output_analysis')
scenarios = len(directories)
sow = 27

# List IDs of structures of interest for output files
IDs = np.genfromtxt('../structures_files/metrics_structures.txt', dtype='str').tolist()
info_clmn = [2, 4, 17]  # Define columns of aspect of interest

if rank == 0:
    for ID in IDs:
        if not os.path.exists('../' + design + '/Infofiles/' + ID):
            os.makedirs('../' + design + '/Infofiles/' + ID)

comm.Barrier()

# Determine the chunk which each processor will need to do
count = int(math.floor(len(IDs) / nprocs))
remainder = len(IDs) % nprocs

# Use the processor rank to determine the chunk of work each processor will do
if rank < remainder:
    start = rank * (count + 1)
    stop = start + count + 1
else:
    start = remainder * (count + 1) + (rank - remainder) * count
    stop = start + count

for k in range(start, stop):
    ID = IDs[k]
    listoffiles = os.listdir('../' + design + '/Infofiles/' + ID)
    files = [x[-13:-4] for x in listoffiles]
    for scenario in directories:
        path = '../' + design + '/Infofiles/' + ID + '/' + ID + '_info_' + scenario + '.txt'
        getinfo(ID, scenario, path, design, sow)
