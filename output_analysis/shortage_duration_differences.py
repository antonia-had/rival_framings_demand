import numpy as np
import matplotlib
from matplotlib import pyplot as plt
plt.switch_backend('agg')
import matplotlib.patches
from scipy import stats
import pandas as pd
import math
from mpi4py import MPI
import sys
import itertools
import glob
import os

plt.ioff()

designs = [str(sys.argv[1]), str(sys.argv[2])]

path = '../' + designs[0] + '_' + designs[1] + '_diff'

all_IDs = ['3600687', '7000550', '7200799', '7200645', '3704614', '7202003']#np.genfromtxt('../structures_files/metrics_structures.txt', dtype='str').tolist()
nStructures = len(all_IDs)

percentiles = np.arange(0, 100)

os.chdir('../' + designs[0])
directories = glob.glob('CMIP*_*')
os.chdir('../output_analysis')
scenarios = len(directories)

sows = [0, 0]

for i in range(len(sows)):
    if designs[i] == 'CMIP_curtailment':
        sows[i] = 27

    else:
        sows[i] = 1

historical = pd.read_csv('../structures_files/shortages.csv', index_col=0)

def alpha(i, base=0.2):
    l = lambda x: x + base - x * base
    ar = [l(0)]
    for j in range(i):
        ar.append(l(ar[-1]))
    return ar[-1]

def shortage_duration(sequence, threshold):
    cnt_shrt = [sequence[i] > threshold for i in
                range(len(sequence))]  # Returns a list of True values when there's a shortage
    shrt_dur = [sum(1 for _ in group) for key, group in itertools.groupby(cnt_shrt) if
                key]  # Counts groups of True values
    return shrt_dur

def plotSDC(syntheticdata, histData,  structure_name):
    n = 12
    # Reshape historic data to a [no. years x no. months] matrix
    f_hist = np.reshape(histData, (int(np.size(histData) / n), n))
    # Reshape to annual totals
    f_hist_totals = np.sum(f_hist, 1)
    # Calculate historical shortage duration curves
    F_hist = np.sort(f_hist_totals)  # for inverse sorting add this at the end [::-1]

    # Reshape synthetic data - repeat for each framing
    # Create matrix of [no. years x no. months x no. samples]
    synthetic_global = [np.zeros([int(len(histData) / n), n, scenarios * sows[0]]),
                        np.zeros([int(len(histData) / n), n, scenarios * sows[1]])]
    synthetic_global_totals = [0]*len(sows)
    F_syn = [np.empty([int(len(histData) / n), scenarios * sows[0]]),
             np.empty([int(len(histData) / n), scenarios * sows[1]])]

    # Calculate synthetic shortage duration curves
    for s in range(len(syntheticdata)):
        F_syn[s][:] = np.NaN
        # Loop through every SOW and reshape to [no. years x no. months]
        for j in range(scenarios * sows[s]):
            synthetic_global[s][:, :, j] = np.reshape(syntheticdata[s][:, j], (int(np.size(syntheticdata[s][:, j]) / n), n))
        # Reshape to annual totals
        synthetic_global_totals[s] = np.sum(synthetic_global[s], 1)
        for j in range(scenarios * sows[s]):
            F_syn[s][:, j] = np.sort(synthetic_global_totals[s][:, j])

    p = np.arange(100, -10, -50)


    # For each percentile of magnitude, calculate the percentile among the experiments ran
    perc_scores = [np.zeros_like(F_syn[0]), np.zeros_like(F_syn[1])]
    for s in range(len(syntheticdata)):
        for m in range(int(len(histData) / n)):
            perc_scores[s][m, :] = [stats.percentileofscore(F_syn[s][m, :], j, 'rank') for j in F_syn[s][m, :]]

    P = np.arange(1., len(histData)/12 + 1) * 100 / (len(histData)/12)

    ylimit = max(np.max(F_syn[0] , np.max(F_syn[1])))
    fig, (ax1) = plt.subplots(1, 1, figsize=(14.5, 8))
    # ax1
    handles = []
    labels = []
    colors = ['#000292', '#BB4430']
    for s in range(len(syntheticdata)):
        for i in range(len(p)):
            ax1.plot(P, np.percentile(F_syn[s][:, :], p[i], axis=1), linewidth=0.7, color=colors[s])

    ax1.plot(P, F_hist, c='black', linewidth=2, label='Historical record')
    ax1.set_ylim(0, ylimit)
    ax1.set_xlim(0, 100)
    ax1.legend(handles=handles, labels=labels, framealpha=1, fontsize=8, loc='upper left',
               title='Frequency in experiment', ncol=2)
    ax1.set_xlabel('Shortage magnitude percentile', fontsize=20)
    ax1.set_ylabel('Annual shortage (Million $m^3$)', fontsize=20)

    fig.suptitle('Shortage magnitudes for ' + structure_name, fontsize=16)
    plt.subplots_adjust(bottom=0.2)
    fig.savefig(path + '/' + structure_name + '.svg')
    fig.savefig(path + '/' + structure_name + '.png')
    fig.clf()

# Begin parallel simulation
comm = MPI.COMM_WORLD

# Get the number of processors and the rank of processors
rank = comm.rank
nprocs = comm.size

# Determine the chunk which each processor will neeed to do
count = int(math.floor(nStructures / nprocs))
remainder = nStructures % nprocs

# Use the processor rank to determine the chunk of work each processor will do
if rank < remainder:
    start = rank * (count + 1)
    stop = start + count + 1
else:
    start = remainder * (count + 1) + (rank - remainder) * count
    stop = start + count

for i in range(start, stop):
    histData = historical.loc[all_IDs[i]].values[-768:] * 1233.4818 / 1000000
    synthetic = [np.zeros([len(histData), scenarios * sows[0]]),
                 np.zeros([len(histData), scenarios * sows[1]])]
    for s in range(len(sows)):
        idx = np.arange(2, sows[s] * 2 + 2, 2)
        for j in range(scenarios):
            path = '../' + designs[s] + '/Infofiles/' + all_IDs[i] + '/' + all_IDs[i] + '_info_' + directories[j] + '.txt'
            data = np.loadtxt(path)
            synthetic[s][:, j * sows[s]:j * sows[s] + sows[s]] = data[:, idx] * 1233.4818 / 1000000
        plotSDC(synthetic, histData, all_IDs[i])


