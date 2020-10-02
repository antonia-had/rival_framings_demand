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

design = str(sys.argv[1])

all_IDs = ['3600687', '7000550', '7200799', '7200645', '3704614', '7202003']#np.genfromtxt('../structures_files/metrics_structures.txt', dtype='str').tolist()
nStructures = len(all_IDs)

percentiles = np.arange(0, 100)

os.chdir('../' + design)
directories = glob.glob('CMIP*_*')
os.chdir('../output_analysis')
scenarios = len(directories)
sow = 27

idx = np.arange(2, 56, 2)

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

def plotSDC(synthetic, structure_name):
    n = 12
    # # Reshape historic data to a [no. years x no. months] matrix
    # f_hist = np.reshape(histData, (int(np.size(histData) / n), n))
    # # Reshape to annual totals
    # f_hist_totals = np.sum(f_hist, 1)
    # # Calculate historical shortage duration curves
    # F_hist = np.sort(f_hist_totals)  # for inverse sorting add this at the end [::-1]

    # Reshape synthetic data
    # Create matrix of [no. years x no. months x no. samples]
    synthetic_global = np.zeros([int(786 / n), n, scenarios * sow])
    # Loop through every SOW and reshape to [no. years x no. months]
    for j in range(scenarios * sow):
        synthetic_global[:, :, j] = np.reshape(synthetic[:, j], (int(np.size(synthetic[:, j]) / n), n))
    # Reshape to annual totals
    synthetic_global_totals = np.sum(synthetic_global, 1)
    print(np.shape(synthetic_global_totals))

    p = np.arange(100, -10, -10)

    # Calculate synthetic shortage duration curves
    F_syn = np.empty([int(786 / n), scenarios * sow])
    F_syn[:] = np.NaN
    for j in range(scenarios * sow):
        F_syn[:, j] = np.sort(synthetic_global_totals[:, j])

    # For each percentile of magnitude, calculate the percentile among the experiments ran
    perc_scores = np.zeros_like(F_syn)
    for m in range(int(786 / n)):
        perc_scores[m, :] = [stats.percentileofscore(F_syn[m, :], j, 'rank') for j in F_syn[m, :]]

    P = np.arange(1., 786/12 + 1) * 100 / 786/12

    ylimit = np.max(F_syn)
    fig, (ax1) = plt.subplots(1, 1, figsize=(14.5, 8))
    # ax1
    handles = []
    labels = []
    color = '#000292'
    for i in range(len(p)):
        ax1.fill_between(P, np.min(F_syn[:, :], 1), np.percentile(F_syn[:, :], p[i], axis=1), color=color, alpha=0.1)
        ax1.plot(P, np.percentile(F_syn[:, :], p[i], axis=1), linewidth=0.5, color=color, alpha=0.3)
        handle = matplotlib.patches.Rectangle((0, 0), 1, 1, color=color, alpha=alpha(i, base=0.1))
        handles.append(handle)
        label = "{:.0f} %".format(100 - p[i])
        labels.append(label)
    #ax1.plot(P, F_hist, c='black', linewidth=2, label='Historical record')
    ax1.set_ylim(0, ylimit)
    ax1.set_xlim(0, 100)
    ax1.legend(handles=handles, labels=labels, framealpha=1, fontsize=8, loc='upper left',
               title='Frequency in experiment', ncol=2)
    ax1.set_xlabel('Shortage magnitude percentile', fontsize=20)
    ax1.set_ylabel('Annual shortage (Million $m^3$)', fontsize=20)

    fig.suptitle('Shortage magnitudes for ' + structure_name, fontsize=16)
    plt.subplots_adjust(bottom=0.2)
    fig.savefig('../' + design + '/ShortagePercentileCurves/' + structure_name + '.svg')
    fig.savefig('../' + design + '/ShortagePercentileCurves/' + structure_name + '.png')
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
    # histData = np.loadtxt('../' + design + '/Infofiles/' + all_IDs[i] + '/' + all_IDs[i] + '_info_0.txt')[:,
    #            2] * 1233.4818 / 1000000
    synthetic = np.zeros([768, scenarios * sow])
    for j in range(scenarios):
        path = '../' + design + '/Infofiles/' + all_IDs[i] + '/' + all_IDs[i] + '_info_' + directories[j] + '.txt'
        data = np.loadtxt(path)
        try:
            synthetic[:, j * sow:j * sow + sow] = data[:, idx] * 1233.4818 / 1000000
        except IndexError:
            print(all_IDs[i] + '_info_' + str(j + 1))
    plotSDC(synthetic, all_IDs[i])


