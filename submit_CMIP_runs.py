from mpi4py import MPI
import math
import os
import glob

os.chdir('../CO_climate_scenarios')
directories = glob.glob('CMIP*_*')
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
    os.chdir('/scratch/ah986/rival_framings_demand/CO_climate_scenarios/'+directories[k]+'/cm2015/StateMod/')
    # # Create symbolic link to statemod executable if not already there
    # if not os.path.isfile("./statemod"):
    #     os.system("ln -s /home/fs02/pmr82_0001/ah986/Colorado/yates_statemod/src/src/main/fortran/statemod .")
    # Run simulation
    os.system("./statemod cm2015B -simulate")
    print ('simulating '+ directories[k])