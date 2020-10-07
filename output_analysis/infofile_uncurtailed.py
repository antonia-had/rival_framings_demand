from mpi4py import MPI
import math
import numpy as np
import os
import sys
import glob

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
print(scenarios)
sow = 27

# List IDs of structures of interest for output files
IDs = ['3600687', '7000550', '7200799', '7200645', '3704614', '7202003']#np.genfromtxt('../Structures_files/metrics_structures.txt', dtype='str').tolist()
info_clmn = [2, 4, 17]  # Define columns of aspect of interest

if rank == 0:
    for ID in IDs:
        if not os.path.exists('../' + design + '/Infofiles/' + ID):
            os.makedirs('../' + design + '/Infofiles/' + ID)

comm.Barrier()

# =============================================================================
# Define output extraction function
# =============================================================================
def getinfo(ID, scenario):
    path = '../' + design + '/Infofiles/' + ID + '/' + ID + '_info_' + scenario + '.txt'
    # Check if infofile doesn't already exist or if size is 0 (remove if wanting to overwrite old files)
    if not (os.path.exists(path) and os.path.getsize(path) > 0):
        lines = []
        if design == 'CMIP_curtailment':
            with open(path, 'w') as f:
                # Read the first SOW separately so the year column is also collected
                with open('../' + design + '/' + scenario + '/cm2015/StateMod/cm2015B_S0.xdd', 'rt') as xdd_file:
                    for line in xdd_file:
                        data = line.split()
                        if data:
                            if data[0] == ID:
                                if data[3] != 'TOT':
                                    lines.append([data[2], data[4], data[17]])
                xdd_file.close()
                for j in range(1, sow):
                    yearcount = 0
                    try:
                        with open('../' + design + '/' + scenario + '/cm2015/StateMod/cm2015B_S' + str(j) + '.xdd',
                                  'rt') as xdd_file:
                            test = xdd_file.readline()
                            if test:
                                for line in xdd_file:
                                    data = line.split()
                                    if data:
                                        if data[0] == ID:
                                            if data[3] != 'TOT':
                                                lines[yearcount].extend([data[4], data[17]])
                                                yearcount += 1
                            else:
                                for i in range(len(lines)):
                                    lines[i].extend(['-999.', '-999.'])
                        xdd_file.close()
                    except IOError:
                        for i in range(len(lines)):
                            lines[i].extend(['-999.', '-999.'])
                for line in lines:
                    for item in line:
                        f.write("%s\t" % item)
                    f.write("\n")
            f.close()
        else:
            with open(path, 'w') as f:
                # Read the first SOW separately so the year column is also collected
                with open('../' + design + '/' + scenario + '/cm2015/StateMod/cm2015B.xdd', 'rt') as xdd_file:
                    for line in xdd_file:
                        data = line.split()
                        if data:
                            if data[0] == ID:
                                if data[3] != 'TOT':
                                    lines.append([data[2], data[4], data[17]])
                xdd_file.close()
                for line in lines:
                    for item in line:
                        f.write("%s\t" % item)
                    f.write("\n")
            f.close()


# Determine the chunk which each processor will need to do
count = int(math.floor(scenarios / nprocs))
remainder = len(IDs) % nprocs

# Use the processor rank to determine the chunk of work each processor will do
if rank < remainder:
    start = rank * (count + 1)
    stop = start + count + 1
else:
    start = remainder * (count + 1) + (rank - remainder) * count
    stop = start + count

for k in range(start, stop):
    scenario = directories[k]
    for ID in IDs:
        getinfo(ID, scenario)
