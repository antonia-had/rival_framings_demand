from mpi4py import MPI
import math
import os

directories = os.listdir('./CMIP_curtailment')
scenarios = len(directories)
# =============================================================================
# Start parallelization
# =============================================================================

# Begin parallel simulation
comm = MPI.COMM_WORLD

# Get the number of processors and the rank of processors
rank = comm.rank
nprocs = comm.size

# Determine the chunk which each processor will need to do
count = int(math.floor(scenarios / nprocs))
remainder = scenarios % nprocs

# Use the processor rank to determine the chunk of work each processor will do
if rank < remainder:
    start = rank * (count + 1)
    stop = start + count + 1
else:
    start = remainder * (count + 1) + (rank - remainder) * count
    stop = start + count

# =============================================================================
# Go though all scenarios
# =============================================================================
for k in range(start, stop):
    # Change to scenario subdirectory
    os.chdir('/scratch/ah986/rival_framings_demand/CMIP_curtailment/'+directories[k]+'/cm2015/StateMod/')
    for i in range(27):
        # Run simulation
        os.system("./statemod cm2015B_S{} -simulate".format(i))
        print ('simulating scenario {} sample {}'.format(directories[k], i))