import os
import pyDOE2
import pandas as pd
from utils import *
from string import Template
from mpi4py import MPI
import math
#import matplotlib.pyplot as plt
#import glob
from realization_flows import realization_monthly_flow

hist_flows = pd.read_csv('./hist_files/AnnualQ.csv',delimiter=',', header=0, index_col=0)
basin_hist_flows = hist_flows['Site208'].values
hist_shortages = np.loadtxt('./hist_files/AnnualShortages.csv', delimiter=',')

'''Get all rights and decrees of each WDID'''
rights = pd.read_csv('./hist_files/iwr_admin.csv')
groupbyadmin = rights.groupby('WDID')
rights_per_wdid = groupbyadmin.apply(lambda x: x['Admin'].values)
decrees_per_wdid = groupbyadmin.apply(lambda x: x['Decree'].values)

shortage_percentile = list(np.arange(80, 110, 10))
no_rights = list(np.arange(30, 120, 30))
curtailment_levels = list(np.arange(30, 120, 30))

sample = pyDOE2.fullfact([3, 3, 3]).astype(int)

# shortage_percentile = list(np.arange(75, 105, 5))
# no_rights = list(np.arange(5, 105, 5))
# curtailment_levels = list(np.arange(5, 105, 5))
#
# sample = pyDOE2.fullfact([6, 20, 20]).astype(int)

numSites = 379

# Use historical shortages and flows to determine trigger flows for curtailment
# trigger_years = [abs(hist_shortages - np.percentile(hist_shortages, p, interpolation='nearest')).argmin() for p in
#                  shortage_percentile]
# trigger_flows = [basin_hist_flows[t] for t in trigger_years]

trigger_flows = [np.percentile(basin_hist_flows, 100 - p, interpolation='nearest') for p in
                  shortage_percentile]

# alphas = np.arange(0.15, 1, 0.15)
# plt.scatter(hist_shortages, basin_hist_flows, c='blue')
# for i in range(len(trigger_flows)):
#     plt.hlines(trigger_flows[i], hist_shortages.min(), hist_shortages.max(),
#                colors='red', alpha = alphas[i])
# plt.show()

# Use rights to determine users and portion to curtail
threshold_admins = [np.percentile(rights['Admin'].values, 100 - p, interpolation='nearest') for p in no_rights]
rights_to_curtail = [rights.loc[rights['Admin'] > t] for t in threshold_admins]
users_per_threshold = [np.unique(rights_to_curtail[x]['WDID'].values) for x in range(len(no_rights))]
curtailment_per_threshold = []
for i in range(len(rights_to_curtail)):
    user_set = rights_to_curtail[i]
    groupbyadmin_curtail = user_set.groupby('WDID')
    decrees_per_wdid_curtail = groupbyadmin_curtail.apply(lambda x: x['Decree'].values)
    curtailment_levels = np.zeros(len(users_per_threshold[i]))
    for j in range(len(users_per_threshold[i])):
        wdid = decrees_per_wdid_curtail.index[j]
        if np.sum(decrees_per_wdid[wdid])!=0:
            curtailment_levels[j] = np.sum(decrees_per_wdid_curtail[wdid]) / np.sum(decrees_per_wdid[wdid])
        else:
            curtailment_levels[j] = 0
    curtailment_per_threshold.append(curtailment_levels)

# sows = np.arange(1, 101, 1)
sows = np.arange(1, 11, 1)
realizations = np.arange(1,11,1)
all_scenarios = ['S'+str(i)+'_'+str(j) for i in sows for j in realizations]

'''Read RSP template'''
T = open('./cm2015B_template.rsp', 'r')
template_RSP = Template(T.read())

# Begin parallel simulation
comm = MPI.COMM_WORLD

# Get the number of processors and the rank of processors
rank = comm.rank
nprocs = comm.size

# Determine the chunk which each processor will need to do
count = int(math.floor(len(all_scenarios) / nprocs))
remainder = len(all_scenarios) % nprocs

# Use the processor rank to determine the chunk of work each processor will do
if rank < remainder:
    start = rank * (count + 1)
    stop = start + count + 1
else:
    start = remainder * (count + 1) + (rank - remainder) * count
    stop = start + count

for scenario in all_scenarios[start:stop]:
    monthly_flows = realization_monthly_flow(scenario)
    annual_flows_scenario = np.sum(monthly_flows, axis=1)
    '''Get data from scenario IWR'''
    firstline_iwr = 463#int(search_string_in_file('../LHsamples_wider_100_AnnQonly/cm2015B_'+scenario+'.iwr', '#>EndHeader')[0]) + 4
    with open('../LHsamples_wider_100_AnnQonly/cm2015B_'+scenario+'.iwr', 'r') as f:
        CMIP_IWR = [x.split() for x in f.readlines()[firstline_iwr:]]
        all_data = [x for x in f.readlines()] # get unsplit data to rewrite firstLine # of rows
        all_split_data = [x.split('.') for x in f.readlines()] # get split data on periods
    f.close()

    '''Get data from scenario DDM'''
    firstline_ddm = 779#int(search_string_in_file('../LHsamples_wider_100_AnnQonly/cm2015B_'+scenario+'.ddm','#>EndHeader')[0]) + 4

    with open('../LHsamples_wider_100_AnnQonly/cm2015B_'+scenario+'.ddm', 'r') as f:
        all_data_DDM = [x for x in f.readlines()]
    f.close()

    # Apply each demand sample to every generator scenario
    for i in range(len(sample[:, 0])):
        # Check if realization run successfully first
        outputfilename = './scenarios/' + scenario + '/cm2015B_' + scenario + '_' + str(i) + '.xdd'
        if not os.path.isfile(outputfilename) and os.path.getsize(outputfilename)< 300*1000000:
            print('generating ' + scenario + '_' + str(i))
            trigger_flow = trigger_flows[sample[i, 0]]
            users = users_per_threshold[sample[i, 1]]
            curtailment_per_user = list(curtailment_per_threshold[sample[i, 1]])
            general_curtailment = curtailment_levels[sample[i, 2]]

            low_flows = annual_flows_scenario <= trigger_flow
            curtailment_years = list(np.arange(1909, 2014)[low_flows])

            writenewIWR(scenario, all_split_data, all_data, firstline_iwr, i, users,
                        curtailment_per_user, general_curtailment, curtailment_years)

            writenewDDM(scenario, all_data_DDM, firstline_ddm, CMIP_IWR, firstline_iwr, i, users,
                        curtailment_years)

            d = {'IWR': 'cm2015B_' + scenario + '_' + str(i) + '.iwr',
                 'DDM': 'cm2015B_' + scenario + '_' + str(i) + '.ddm'}
            S1 = template_RSP.safe_substitute(d)
            f1 = open('./scenarios/' + scenario + '/cm2015B_' + scenario + '_' + str(i) + '.rsp', 'w')
            f1.write(S1)
            f1.close()
