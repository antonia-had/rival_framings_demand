import os
import numpy as np
import matplotlib.pyplot as plt
from utils import search_string_in_file
import glob

numSites = 379

def realization_monthly_flow(realization):
    file = open('../LHsamples_wider_100_AnnQonly/cm2015x_'+realization+'.xbm', 'r')
    all_split_data = [x.split('.') for x in file.readlines()]
    file.close()
    yearcount = 0
    flows = np.zeros([64, 12])
    for i in range(16, len(all_split_data)):
        row_data = []
        row_data.extend(all_split_data[i][0].split())
        if row_data[1] == '09163500':
            if int(row_data[0]) >= 1950:
                data_to_write = [row_data[2]] + all_split_data[i][1:12]
                flows[yearcount, :] = [int(n) for n in data_to_write]
                yearcount += 1
    np.savetxt('./scenarios/' + realization + '/' + realization + '_MonthlyFlows.csv', flows, fmt='%d', delimiter=',')
    return flows