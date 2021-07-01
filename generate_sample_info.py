import pyDOE2
import pandas as pd
import numpy as np
import pickle

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
np.savetxt('curtailment_levels.txt', curtailment_levels)

sample = pyDOE2.fullfact([3, 3, 3]).astype(int)
np.savetxt('factorial_sample.txt', sample)

numSites = 379

trigger_flows = [np.percentile(basin_hist_flows, 100 - p, interpolation='nearest') for p in
                  shortage_percentile]
np.savetxt('trigger_flows.txt', trigger_flows)

# Use rights to determine users and portion to curtail
threshold_admins = [np.percentile(rights['Admin'].values, 100 - p, interpolation='nearest') for p in no_rights]
rights_to_curtail = [rights.loc[rights['Admin'] > t] for t in threshold_admins]
users_per_threshold = [np.unique(rights_to_curtail[x]['WDID'].values) for x in range(len(no_rights))]
with open("users_per_threshold.pkl", "wb") as fp:
    pickle.dump(users_per_threshold, fp)
curtailment_per_threshold = []
for i in range(len(rights_to_curtail)):
    user_set = rights_to_curtail[i]
    groupbyadmin_curtail = user_set.groupby('WDID')
    decrees_per_wdid_curtail = groupbyadmin_curtail.apply(lambda x: x['Decree'].values)
    curtailment_levels_users = np.zeros(len(users_per_threshold[i]))
    for j in range(len(users_per_threshold[i])):
        wdid = decrees_per_wdid_curtail.index[j]
        if np.sum(decrees_per_wdid[wdid]) != 0:
            curtailment_levels_users[j] = np.sum(decrees_per_wdid_curtail[wdid]) / np.sum(decrees_per_wdid[wdid])
        else:
            curtailment_levels_users[j] = 0
    curtailment_per_threshold.append(curtailment_levels_users)
with open("curtailment_per_threshold.pkl", "wb") as fp:
    pickle.dump(curtailment_per_threshold, fp)