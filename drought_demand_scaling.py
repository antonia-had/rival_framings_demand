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
rights = pd.read_csv('./hist_files/iwr_admin.csv')

shortage_percentile = [100, 95, 90]
no_users = [2, 5, 10]
curtailment_levels = [20, 50, 100]

sample = pyDOE2.fullfact([3, 3, 3])

numSites = 379

# Use historical shortages and flows to determine trigger flows for curtailment
trigger_years = [abs(hist_shortages-np.percentile(hist_shortages, p, interpolation='nearest')).argmin() for p in shortage_percentile]
trigger_flows = [annual_flows[t] for t in trigger_years]

# Use rights to determine users to curtail
threshold_admins = [np.percentile(rights['Admin'].values, 100-p, interpolation='nearest') for p in no_users]
users_to_curtail = [rights.loc[rights['Admin'] > t]['WDID'].values for t in threshold_admins]

listofyears = np.arange(1950,2013)

for scenario in directories[:1]:
    monthly_flows = np.loadtxt('./CMIP_scenarios/' + scenario + '/MonthlyFlows.csv', delimiter=',')
    annual_flows_scenario = np.sum(monthly_flows, axis=1)
    # Apply each sample to every CMIP scenario
    for i in range(len(3)):#sample[:,0])):
        trigger_flow = trigger_flows[sample[i,0]]
        users = users_to_curtail[sample[i,1]]
        curtailment = curtailment_levels[sample[i,2]]

        low_flows = annual_flows <= trigger_flow
        curtailment_years = np.arange(1950,2014)[low_flows]

        writenewIWR(scenario, 'cm2015B.iwr', 463, i, users, curtailment, curtailment_years)
