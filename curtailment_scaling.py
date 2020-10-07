import os
import pyDOE2
import pandas as pd
from utils import *
from string import Template
from mpi4py import MPI
import math
import glob

os.chdir('./CMIP_curtailment')
directories = glob.glob('CMIP*_*')
os.chdir('..')
scenarios = 1#len(directories)

hist_iwr = np.loadtxt('./hist_files/MonthlyIWR.csv', delimiter=',')
hist_flows = np.loadtxt('./hist_files/MonthlyFlows.csv', delimiter=',')
annual_flows = np.sum(hist_flows, axis=1)
hist_shortages = np.loadtxt('./hist_files/annual_shortages.csv', delimiter=',')

'''Get all rights and decrees of each WDID'''
rights = pd.read_csv('./hist_files/iwr_admin.csv')
groupbyadmin = rights.groupby('WDID')
rights_per_wdid = groupbyadmin.apply(lambda x: x['Admin'].values)
decrees_per_wdid = groupbyadmin.apply(lambda x: x['Decree'].values)

shortage_percentile = [100, 95, 90]
no_rights = [5, 10, 20]
curtailment_levels = [20, 50, 100]

sample = pyDOE2.fullfact([3, 3, 3]).astype(int)

numSites = 379

# Use historical shortages and flows to determine trigger flows for curtailment
trigger_years = [abs(hist_shortages - np.percentile(hist_shortages, p, interpolation='nearest')).argmin() for p in
                 shortage_percentile]
trigger_flows = [annual_flows[t] for t in trigger_years]

# Use rights to determine users and portion to curtail
threshold_admins = [np.percentile(rights['Admin'].values, 100 - p, interpolation='nearest') for p in no_rights]
rights_to_curtail = [rights.loc[rights['Admin'] > t] for t in threshold_admins]
users_per_threshold = [np.unique(rights_to_curtail[x]['WDID'].values) for x in range(3)]
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

list_of_years = np.arange(1950, 2013)

'''Read RSP template'''
T = open('./cm2015B_template.rsp', 'r')
template_RSP = Template(T.read())

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

for scenario in directories[start:stop]:
    monthly_flows = np.loadtxt('./CMIP_scenarios/' + scenario + '/MonthlyFlows.csv', delimiter=',')
    annual_flows_scenario = np.sum(monthly_flows, axis=1)

    '''Get data from original scenario IWR'''
    firstline_iwr = int(
        search_string_in_file('./CMIP_scenarios/' + scenario + '/cm2015/StateMod/cm2015B.iwr', '#>EndHeader')[0]) + 4

    with open('./CMIP_scenarios/' + scenario + '/cm2015/StateMod/cm2015B.iwr', 'r') as f:
        CMIP_IWR = [x.split() for x in f.readlines()[firstline_iwr:]]
    f.close()

    # get unsplit data to rewrite firstLine # of rows
    # get split data on periods
    with open('./CMIP_scenarios/' + scenario + '/cm2015/StateMod/cm2015B.iwr', 'r') as f:
        all_data = [x for x in f.readlines()]
    f.close()

    with open('./CMIP_scenarios/' + scenario + '/cm2015/StateMod/cm2015B.iwr', 'r') as f:
        all_split_data = [x.split('.') for x in f.readlines()]
    f.close()

    '''Get data from original scenario DDM'''
    firstline_ddm = int(
        search_string_in_file('./CMIP_scenarios/' + scenario + '/cm2015/StateMod/cm2015B.ddm',
                              '#>EndHeader')[0]) + 4

    with open('./CMIP_scenarios/' + scenario + '/cm2015/StateMod/cm2015B.ddm', 'r') as f:
        all_data_DDM = [x for x in f.readlines()]
    f.close()

    # Apply each sample to every CMIP scenario
    for i in range(len(sample[:, 0])):
        trigger_flow = trigger_flows[sample[i, 0]]
        users = users_per_threshold[sample[i, 1]]
        curtailment_per_user = list(curtailment_per_threshold[sample[i, 1]])
        general_curtailment = curtailment_levels[sample[i, 2]]

        low_flows = annual_flows_scenario <= trigger_flow
        curtailment_years = list(np.arange(1950, 2014)[low_flows])

        writenewIWR(scenario, all_split_data, all_data, firstline_iwr, i, users,
                    curtailment_per_user, general_curtailment, curtailment_years)

        writenewDDM(scenario, all_data_DDM, firstline_ddm, CMIP_IWR, firstline_iwr, i, users,
                    curtailment_years)

        d = {'IWR': 'cm2015B_S' + str(i) + '.iwr',
             'DDM': 'cm2015B_S' + str(i) + '.ddm'}
        S1 = template_RSP.safe_substitute(d)
        f1 = open('./CMIP_curtailment/' + scenario + '/cm2015/StateMod/cm2015B_S' + str(i) + '.rsp', 'w')
        f1.write(S1)
        f1.close()
