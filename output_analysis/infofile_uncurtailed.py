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
sow = 27

# List IDs of structures of interest for output files
IDs = np.genfromtxt('../structures_files/metrics_structures.txt', dtype='str').tolist()
info_clmn = [2, 4, 17]  # Define columns of aspect of interest

if rank == 0:
    for ID in IDs:
        if not os.path.exists('../' + design + '/Infofiles/' + ID):
            os.makedirs('../' + design + '/Infofiles/' + ID)

comm.Barrier()
with open("../debugged_runs.txt") as f:
    missing_infofiles = f.read().splitlines()
f.close()


# =============================================================================
# Define output extraction function
# =============================================================================
def getinfo(ID, scenario, path):
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
    wdid = IDs[k]
    listoffiles = os.listdir('../' + design + '/Infofiles/' + ID)
    files = [x[-13:-4] for x in listoffiles]
    for scenario in directories:
        path = '../' + design + '/Infofiles/' + ID + '/' + ID + '_info_' + scenario + '.txt'
        # If infofile for scenario was never created
        if scenario not in files:
            print(scenario+'_'+ID)
            getinfo(ID, scenario, path)
        else:
            # If infofile was created but it was in the bugged out SOWs
            if scenario in missing_infofiles:
                # Check creation time and size
                [mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime] = os.stat(path)
                # If it was created before Oct 20 or never written into
                if mtime < 1603188171 or size < 10:
                    print(scenario+'_'+ID)
                    getinfo(ID, scenario, path)
