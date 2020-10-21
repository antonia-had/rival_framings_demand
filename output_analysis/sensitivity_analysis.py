import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.anova import anova_lm
import scipy.stats
import matplotlib.pyplot as plt
import math
import pyDOE2
import glob
import os
from mpi4py import MPI

plt.ioff()

design = 'CMIP_curtailment'
directories = glob.glob('../' + design + '/CMIP*_*')

SOWsample = pyDOE2.fullfact([3, 3, 3, len(directories)]).astype(int)
samples = len(SOWsample[:, 0])
params_no = len(SOWsample[0, :])
realizations = int(samples/len(directories))
idx = np.arange(2, realizations*2+2, 2)

param_names = ['Shortage trigger', 'Percent of rights', 'Curtailment level', 'CMIP scenario']

percentiles = np.arange(0, 100)
all_IDs = np.genfromtxt('../structures_files/metrics_structures.txt', dtype='str').tolist()
nStructures = len(all_IDs)

no_months = 768
n = 12

def fitOLS(dta, predictors):
    # concatenate intercept column of 1s
    dta['Intercept'] = np.ones(np.shape(dta)[0])
    # get columns of predictors
    cols = dta.columns.tolist()[-1:] + predictors
    # fit OLS regression
    ols = sm.OLS(dta['Shortage'], dta[cols])
    result = ols.fit()
    return result

def collect_experiment_data(ID):
    summary_file_path = '../' + design + '/Infofiles/' + ID + '/' + ID + '_all.txt'
    if os.path.exists(summary_file_path):
        SYN_short = np.loadtxt(summary_file_path)
    else:
        SYN_short = np.zeros([len(no_months), samples])
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

def ANOVA_sensitivity_analysis(model_output):
    '''
    Perform analysis for shortage magnitude
    '''
    SI = pd.DataFrame(np.zeros((params_no, len(percentiles))), columns=percentiles)
    SI.index = param_names

    # Delta Method analysis
    for i in range(len(percentiles)):
        if syn_magnitude[i, :].any():
            try:
                output = np.mean(syn_magnitude[i, :].reshape(-1, 10), axis=1)
                output = output[rows_to_keep]
                result = delta.analyze(problem, LHsamples, output, print_to_console=False, num_resamples=10)
                DELTA[percentiles[i]] = result['delta']
                DELTA_conf[percentiles[i]] = result['delta_conf']
                S1[percentiles[i]] = result['S1']
                S1_conf[percentiles[i]] = result['S1_conf']
            except:
                pass

    S1.to_csv('../' + design + '/Magnitude_Sensitivity_analysis/' + ID + '_S1.csv')
    S1_conf.to_csv('../' + design + '/Magnitude_Sensitivity_analysis/' + ID + '_S1_conf.csv')
    DELTA.to_csv('../' + design + '/Magnitude_Sensitivity_analysis/' + ID + '_DELTA.csv')
    DELTA_conf.to_csv('../' + design + '/Magnitude_Sensitivity_analysis/' + ID + '_DELTA_conf.csv')

    # OLS regression analysis
    dta = pd.DataFrame(data=LHsamples, columns=param_names)
    for i in range(len(percentiles)):
        output = np.mean(syn_magnitude[i, :].reshape(-1, 10), axis=1)
        dta['Shortage'] = output[rows_to_keep]
        for m in range(params_no):
            predictors = dta.columns.tolist()[m:(m + 1)]
            result = fitOLS(dta, predictors)
            R2_scores.at[param_names[m], percentiles[i]] = result.rsquared
    R2_scores.to_csv('../' + design + '/Magnitude_Sensitivity_analysis/' + ID + '_R2.csv')


# =============================================================================
# Start parallelization (running each structure in parallel)
# =============================================================================

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

# Run simulation
for k in range(start, stop):
    model_output = collect_experiment_data(all_IDs[k])
    ANOVA_sensitivity_analysis(model_output)