import numpy as np
import pandas as pd
from statsmodels.formula.api import ols
from statsmodels.stats.api import anova_lm
import math
import pyDOE2
import glob
import os
from mpi4py import MPI

design = 'CMIP_curtailment'
directories = glob.glob('../' + design + '/CMIP*_*')
directories = [x[-9:] for x in directories]

SOWsample = pyDOE2.fullfact([3, 3, 3, len(directories)]).astype(int)
samples = len(SOWsample[:, 0])
params_no = len(SOWsample[0, :])
realizations = int(samples/len(directories))
idx = np.arange(2, realizations*2+2, 2)

param_names = ['Shortage_trigger', 'Percent_rights', 'Curtailment_level', 'CMIP_scenario']

percentiles = np.arange(0, 100)
all_IDs = ['3600687', '7000550', '7200799', '7200645', '3704614', '7202003']#np.genfromtxt('../structures_files/metrics_structures.txt', dtype='str').tolist()
nStructures = len(all_IDs)

no_months = 768
n = 12

#Statsmodels OLS formula
formula = 'Shortage ~ C(Shortage_trigger) + C(Percent_rights) + C(Curtailment_level) + C(CMIP_scenario) + \
        C(Shortage_trigger):C(Percent_rights) + C(Shortage_trigger):C(Curtailment_level) + \
        C(Percent_rights):C(Curtailment_level) + C(Shortage_trigger):C(CMIP_scenario) + \
        C(Percent_rights):C(CMIP_scenario) + C(Curtailment_level):C(CMIP_scenario)'

def collect_experiment_data(ID):
    summary_file_path = '../' + design + '/Infofiles/' + ID + '/' + ID + '_all.txt'
    if os.path.exists(summary_file_path):
        SYN_short = np.loadtxt(summary_file_path)
    else:
        SYN_short = np.zeros([no_months, samples])
        for j in range(int(samples/realizations)):
            infofile_path = '../' + design + '/Infofiles/' + ID + '/' + ID + '_info_' + directories[j] + '.txt'
            data = np.loadtxt(infofile_path)
            try:
                SYN_short[:, j * realizations:j * realizations + realizations] = data[:, idx]
            except IndexError:
                print('IndexError ' + ID + '_info_' + str(j))
        np.savetxt(summary_file_path, SYN_short)
    # Reshape into water years
    # Create matrix of [no. years x no. months x no. experiments]
    f_SYN_short = np.zeros([int(no_months / n), n, samples])
    for i in range(samples):
        f_SYN_short[:, :, i] = np.reshape(SYN_short[:, i], (int(np.size(SYN_short[:, i]) / n), n))
    # Shortage per water year
    f_SYN_short_WY = np.sum(f_SYN_short, axis=1)
    # Identify shortages at percentiles
    syn_magnitude = np.zeros([len(percentiles), samples])
    for j in range(samples):
        syn_magnitude[:, j] = [np.percentile(f_SYN_short_WY[:, j], i) for i in percentiles]
    return syn_magnitude

def ANOVA_sensitivity_analysis(ID, syn_magnitude):
    '''
    Perform analysis for shortage magnitude
    '''
    SI = pd.DataFrame(np.zeros((11, len(percentiles))), columns = percentiles)
    p_values = pd.DataFrame(np.zeros((11, len(percentiles))), columns = percentiles)
    # ANOVA
    dta = pd.DataFrame(data=SOWsample, columns=param_names)
    for i in range(len(percentiles)):
        dta['Shortage'] = syn_magnitude[i, :]
        shortage_lm = ols(formula, data=dta).fit()
        table = anova_lm(shortage_lm)
        ss_values = table['sum_sq'].values
        SI[percentiles[i]] = ss_values/np.sum(ss_values)
        p_values[percentiles[i]] = table['PR(>F)'].values
    SI.index = p_values.index = table.index
    SI.to_csv('../' + design + '/Magnitude_Sensitivity_analysis/' + ID + '_SI.csv')
    p_values.to_csv('../' + design + '/Magnitude_Sensitivity_analysis/' + ID + '_p_values.csv')

# =============================================================================
# Start parallelization (running each structure in parallel)
# =============================================================================

# Begin parallel simulation
comm = MPI.COMM_WORLD

# Get the number of processors and the rank of processors
rank = comm.rank
nprocs = comm.size

# Determine the chunk which each processor will need to do
count = int(math.floor(nStructures / nprocs))
remainder = nStructures % nprocs

# Use the processor rank to determine the chunk of work each processor will do
if rank < remainder:
    start = rank * (count + 1)
    stop = start + count + 1
else:
    start = remainder * (count + 1) + (rank - remainder) * count
    stop = start + count

# Run simulation
for k in range(start, stop):
    syn_magnitude = collect_experiment_data(all_IDs[k])
    ANOVA_sensitivity_analysis(all_IDs[k], syn_magnitude)