import os
import pyDOE2
import numpy as np
import pandas as pd
from utils import writenewIWR

directories = os.listdir('./CMIP_curtailment')
scenarios = len(directories)

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
no_rights = [2, 5, 10]
curtailment_levels = [20, 50, 100]

sample = pyDOE2.fullfact([3, 3, 3]).astype(int)

numSites = 379

# Use historical shortages and flows to determine trigger flows for curtailment
trigger_years = [abs(hist_shortages-np.percentile(hist_shortages, p, interpolation='nearest')).argmin() for p in shortage_percentile]
trigger_flows = [annual_flows[t] for t in trigger_years]

# Use rights to determine users and portion to curtail
threshold_admins = [np.percentile(rights['Admin'].values, 100-p, interpolation='nearest') for p in no_rights]
rights_to_curtail = [rights.loc[rights['Admin'] > t] for t in threshold_admins]
users_per_threshold = [np.unique(rights_to_curtail[x]['WDID'].values) for x in range(3)]
curtailment_per_threshold = []
for i in range(len(rights_to_curtail)):
    user_set = rights_to_curtail[i]
    groupbyadmin_curtail = user_set.groupby('WDID')
    decrees_per_wdid_curtail = groupbyadmin_curtail.apply(lambda x: x['Decree'].values)
    curtailment_levels = np.zeros(len(users_per_threshold[i]))
    for j in range(len(users_per_threshold[i])):
        wdid=decrees_per_wdid_curtail.index[j]
        curtailment_levels[j] = np.sum(decrees_per_wdid_curtail[wdid])/np.sum(decrees_per_wdid[wdid])
    curtailment_per_threshold.append(curtailment_levels)

listofyears = np.arange(1950,2013)

for scenario in directories[:1]:
    monthly_flows = np.loadtxt('./CMIP_scenarios/' + scenario + '/MonthlyFlows.csv', delimiter=',')
    annual_flows_scenario = np.sum(monthly_flows, axis=1)
    # Apply each sample to every CMIP scenario
    for i in range(1):#len(sample[:,0])):
        trigger_flow = trigger_flows[sample[i,0]]
        users = list(users_per_threshold[sample[i,1]])
        curtailment_per_user = list(curtailment_per_threshold[sample[i,1]])
        general_curtailment = curtailment_levels[sample[i,2]]

        low_flows = annual_flows <= trigger_flow
        curtailment_years = list(np.arange(1950,2014)[low_flows])

        writenewIWR(scenario, 'cm2015B.iwr', i, users, curtailment_per_user, general_curtailment, curtailment_years)
