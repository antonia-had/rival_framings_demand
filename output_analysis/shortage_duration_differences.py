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
import os

plt.ioff()

original_design = 'LHsamples_wider_1000_AnnQonly'
alternative_design = 'CMIP_curtailment'
scenarios = [1000, 209]
realizations = [20, 27]

figures_path = '../' + original_design + '_' + alternative_design + '_diff'

all_IDs = ['3600687', '7000550', '7200799', '7200645', '3704614', '7202003']#np.genfromtxt('../structures_files/metrics_structures.txt', dtype='str').tolist()
nStructures = len(all_IDs)

percentiles = np.arange(0, 100)

historical = pd.read_csv('../structures_files/shortages.csv', index_col=0)

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
    synthetic_global = [np.zeros([int(len(histData) / n), n, scenarios[0] * realizations[0]]),
                        np.zeros([int(len(histData) / n), n, scenarios[1] * realizations[1]])]
    synthetic_global_totals = [0]*len(realizations)
    F_syn = [np.empty([int(len(histData) / n), scenarios[0] * realizations[0]]),
             np.empty([int(len(histData) / n), scenarios[1] * realizations[1]])]

    # Calculate synthetic shortage duration curves
    for s in range(len(syntheticdata)):
        F_syn[s][:] = np.NaN
        # Loop through every SOW and reshape to [no. years x no. months]
        for j in range(scenarios[s] * realizations[s]):
            synthetic_global[s][:, :, j] = np.reshape(syntheticdata[s][:, j], (int(np.size(syntheticdata[s][:, j]) / n), n))
        # Reshape to annual totals
        synthetic_global_totals[s] = np.sum(synthetic_global[s], 1)
        for j in range(scenarios[s] * realizations[s]):
            F_syn[s][:, j] = np.sort(synthetic_global_totals[s][:, j])

    p = np.arange(100, -10, -50)


    # For each percentile of magnitude, calculate the percentile among the experiments ran
    perc_scores = [np.zeros_like(F_syn[0]), np.zeros_like(F_syn[1])]
    for s in range(len(syntheticdata)):
        for m in range(int(len(histData) / n)):
            perc_scores[s][m, :] = [stats.percentileofscore(F_syn[s][m, :], j, 'rank') for j in F_syn[s][m, :]]

    P = np.arange(1., len(histData)/12 + 1) * 100 / (len(histData)/12)

    ylimit = max(np.max(F_syn[0]) , np.max(F_syn[1]), np.max(F_hist))
    fig, (ax1) = plt.subplots(1, 1, figsize=(14.5, 8))
    # ax1
    handles = []
    labels = []
    colors = ['#000292', '#BB4430']
    for i in range(len(p)):
        ax1.fill_between(P, y1=np.percentile(F_syn[0][:, :], p[i], axis=1),
                         y2=np.percentile(F_syn[1][:, :], p[i], axis=1),
                         where=np.percentile(F_syn[0][:, :], p[i], axis=1) > np.percentile(F_syn[1][:, :], p[i], axis=1),
                         interpolate=True, color=colors[0], alpha=0.5)
        ax1.fill_between(P, y1=np.percentile(F_syn[1][:, :], p[i], axis=1),
                         y2=np.percentile(F_syn[0][:, :], p[i], axis=1),
                         where=np.percentile(F_syn[1][:, :], p[i], axis=1) > np.percentile(F_syn[0][:, :], p[i], axis=1),
                         interpolate=True, color=colors[1], alpha=0.5)
        for s in range(len(syntheticdata)):
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
    fig.savefig(figures_path + '/' + structure_name + '.svg')
    fig.savefig(figures_path + '/' + structure_name + '.png')
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
    synthetic = [0] * 2
    summary_file_paths = ['../../' + original_design + '/Infofiles/' + all_IDs[i] + '_info.npy',
                          '../' + alternative_design + '/Infofiles/' + all_IDs[i] + '/' + all_IDs[i] + '_all.txt']
    SYN_short = np.load(summary_file_paths[0])
    synthetic[0] = SYN_short[-768:, 1:, :]
    print(np.shape(synthetic[0]))
    SYN_short = np.loadtxt(summary_file_paths[1])
    synthetic[1] = SYN_short[-768:]
    print(np.shape(synthetic[1]))
    #plotSDC(synthetic, histData, all_IDs[i])


