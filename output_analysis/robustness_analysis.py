import numpy as np
import scipy.stats
import matplotlib as mpl
import matplotlib.pyplot as plt 
plt.switch_backend('agg')
from mpi4py import MPI
import math
import os
plt.ioff()
import sys
import glob
import pandas as pd

# =============================================================================
# Experiment set up
# =============================================================================
design = str(sys.argv[1])

os.chdir('../' + design)
directories = glob.glob('CMIP*_*')
os.chdir('../output_analysis')
scenarios = len(directories)

if design == 'CMIP_curtailment':
    sow = 27

else:
    sow = 1

idx_shortage = np.arange(2, sow*2+2, 2)
idx_demand = np.arange(1,sow*2+1,2)

all_IDs = ['3600687', '7000550', '7200799', '7200645', '3704614', '7202003']#np.genfromtxt('../structures_files/metrics_structures.txt', dtype='str').tolist()
nStructures = len(all_IDs)

historical_shortages = pd.read_csv('../structures_files/shortages.csv', index_col=0)
historical_demands = pd.read_csv('../structures_files/demands.csv', index_col=0)

n=12 # Number of months in a year for reshaping data
nMonths = 768

# Set arrays for shortage frequencies and magnitudes
frequencies = np.arange(10, 110, 10)
magnitudes = np.arange(10, 110, 10)
streamdemand = np.array([1950, 1750, 1630, 1450, 1240, 1150, 950, 810, 650, 500])*60.3707

def roundup(x):
    return int(math.ceil(x / 10.0)) * 10

def highlight_cell(x,y, ax=None, **kwargs):
    rect = plt.Rectangle((x-.5, y-.5), 1,1, fill=False, **kwargs)
    ax = ax or plt.gca()
    ax.add_patch(rect)
    return rect

def plotfailureheatmap(ID):
    if ID == '7202003':
        streamflow = np.zeros([nMonths,scenarios*sow])
        
        for j in range(scenarios):
            data = np.loadtxt('../'+design+'/Infofiles/' +\
                             ID + '/' + ID + '_streamflow_' + directories[j] + '.txt')[:, 1:]
            streamflow[:, j*sow:j*sow+sow] = data
        
        # streamflowhistoric = np.loadtxt('../'+design+'/Infofiles/' +\
        #                                 ID + '/' + ID + '_streamflow_0.txt')[:,1]
        #
        # historic_percents = [100-scipy.stats.percentileofscore(streamflowhistoric, dem, kind='strict') for dem in streamdemand]

        percentSOWs = np.zeros([len(frequencies), len(streamdemand)])
        allSOWs = np.zeros([len(frequencies), len(streamdemand), scenarios * sow])
        
        for j in range(len(frequencies)):
            for h in range(len(streamdemand)):
                success = np.zeros(scenarios*sow)
                for k in range(len(success)):
                    if 100 - scipy.stats.percentileofscore(streamflow[:,k], streamdemand[h], kind='strict')>(100-frequencies[j]):
                        success[k]=100
                allSOWs[j,h,:]=success
                percentSOWs[j,h]=np.mean(success)
        gridcells = []
        # for x in historic_percents:
        #     try:
        #         gridcells.append(list(frequencies)[::-1].index(roundup(x)))
        #     except:
        #         gridcells.append(0)
        
    else:                     
        historic_demands = historical_demands.loc[ID].values[-768:] * 1233.4818 / 1000000
        historic_shortages = historical_shortages.loc[ID].values[-768:] * 1233.4818 / 1000000
        #reshape into water years
        historic_shortages_f= np.reshape(historic_shortages, (int(np.size(historic_shortages)/n), n))
        historic_demands_f= np.reshape(historic_demands, (int(np.size(historic_demands)/n), n))
        
        historic_demands_f_WY = np.sum(historic_demands_f,axis=1)
        historic_shortages_f_WY = np.sum(historic_shortages_f,axis=1)
        historic_ratio = (historic_shortages_f_WY*100)/historic_demands_f_WY
        historic_percents = [100-scipy.stats.percentileofscore(historic_ratio, mag, kind='strict') for mag in magnitudes]
        
        percentSOWs = np.zeros([len(frequencies), len(magnitudes)])
        allSOWs = np.zeros([len(frequencies), len(magnitudes), scenarios*sow])
        
        shortages = np.zeros([nMonths , scenarios*sow])
        demands = np.zeros([nMonths , scenarios*sow])
        for j in range(scenarios):
            data= np.loadtxt('../'+design+'/Infofiles/' + ID + '/' + ID + '_info_' + directories[j] + '.txt')
            try:
                demands[:, j*sow:j*sow+sow] = data[:, idx_demand]
                shortages[:, j*sow:j*sow+sow] = data[:, idx_shortage]
            except:
                print('problem with ' + ID + '_info_' + str(j+1))
                
        #Reshape into water years
        #Create matrix of [no. years x no. months x no. experiments]
        f_shortages = np.zeros([int(nMonths/n), n ,scenarios*sow])
        f_demands = np.zeros([int(nMonths/n), n ,scenarios*sow])
        for i in range(scenarios*sow):
            f_shortages[:,:,i]= np.reshape(shortages[:,i], (int(np.size(shortages[:,i])/n), n))
            f_demands[:,:,i]= np.reshape(demands[:,i], (int(np.size(demands[:,i])/n), n))
        
        # Shortage per water year
        f_demands_WY = np.sum(f_demands,axis=1)
        f_shortages_WY = np.sum(f_shortages,axis=1)
        for j in range(len(frequencies)):
            for h in range(len(magnitudes)):
                success = np.zeros(scenarios*sow)
                for k in range(len(success)):
                    ratio = (f_shortages_WY[:,k]*100)/f_demands_WY[:,k]
                    if scipy.stats.percentileofscore(ratio, magnitudes[h], kind='strict')>(100-frequencies[j]):
                        success[k]=100
                allSOWs[j,h,:]=success
                percentSOWs[j,h]=np.mean(success)
                
        gridcells = []
        for x in historic_percents:
            try:
                gridcells.append(list(frequencies).index(roundup(x)))
            except:
                gridcells.append(0)
    
    fig, ax = plt.subplots()
    print(np.amax(percentSOWs))
    im = ax.imshow(percentSOWs, norm = mpl.colors.Normalize(vmin=0.0,vmax=100.0), cmap='RdBu', interpolation='nearest')
#    for j in range(len(frequencies)):
#        for h in range(len(magnitudes)):
#            ax.text(h, j, int(percentSOWs[j,h]),
#                           ha="center", va="center", color="w")
    
    if ID =='7202003':
        ax.set_xticks(np.arange(len(streamdemand)))
        ax.set_xticklabels([str(int(x/60.3707)) for x in list(streamdemand)])
        ax.set_xlabel("Streamflow to meet (cfs)")
        ax.set_ylabel("Percent of time flow is met")
        ax.set_yticks(np.arange(len(frequencies)))
        ax.set_yticklabels([str(x) for x in list(frequencies)[::-1]])        
    else:
        ax.set_xticks(np.arange(len(magnitudes)))
        ax.set_xticklabels([str(x) for x in list(magnitudes)])
        ax.set_xlabel("Percent of demand that is short")
        ax.set_ylabel("Percent of time shortage is experienced")
        ax.set_yticks(np.arange(len(frequencies)))
        ax.set_yticklabels([str(x) for x in list(frequencies)])
        
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    for edge, spine in ax.spines.items():
        spine.set_visible(False)

    ax.set_xticks(np.arange(percentSOWs.shape[1]+1)-.5, minor=True)
    ax.set_yticks(np.arange(percentSOWs.shape[0]+1)-.5, minor=True)
    #ax.grid(which="minor", color="w", linestyle='-', linewidth=1)
    ax.tick_params(which="minor", bottom=False, left=False)
    
    cbar = ax.figure.colorbar(im, ax=ax, cmap='RdBu')
    cbar.ax.set_ylabel("Percentage of SOWs where criterion was met", rotation=-90, va="bottom")
    
    for i in range(len(historic_percents)):
        if historic_percents[i]!=0:
            highlight_cell(i,gridcells[i], color="orange", linewidth=4)
    
    fig.tight_layout()
    fig.savefig('../'+design+'/Robustness/Heatmaps/'+ID+'.svg')
    plt.close()
    
    np.save('../'+design+'/Robustness/'+ ID + '_heatmap.npy', allSOWs)
    
    return(allSOWs, historic_percents)

#def shortage_duration(sequence, value):
#    cnt_shrt = [sequence[i]>value for i in range(len(sequence))] # Returns a list of True values when there's a shortage about the value
#    shrt_dur = [ sum( 1 for _ in group ) for key, group in itertools.groupby( cnt_shrt ) if key ] # Counts groups of True values
#    return shrt_dur

    
# Begin parallel simulation
comm = MPI.COMM_WORLD

# Get the number of processors and the rank of processors
rank = comm.rank
nprocs = comm.size

# Determine the chunk which each processor will neeed to do
count = int(math.floor(nStructures/nprocs))
remainder = nStructures % nprocs

# Use the processor rank to determine the chunk of work each processor will do
if rank < remainder:
	start = rank*(count+1)
	stop = start + count + 1
else:
	start = remainder*(count+1) + (rank-remainder)*count
	stop = start + count
    
# Run simulation
for i in range(start, stop):
    plotfailureheatmap(all_IDs[i])