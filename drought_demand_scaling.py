import os
import pyDOE2
from utils import search_string_in_file
import numpy as np


directories = os.listdir('./CMIP_curtailment')
scenarios = len(directories)

shortage_levels = [10, 20, 30]
no_users = [2, 5, 10]
curtailment = [20, 50, 100]
duration = [1, 2, 5]

sample = pyDOE2.fullfact([3, 3, 3, 3])

numSites = 379

def monthly_iwr(scenario):
    filename = './CMIP_scenarios/' + scenario + '/cm2015/StateMod/cm2015'
    firstline = int(search_string_in_file(filename + 'B.iwr', '#>EndHeader')[0]) + 4

    # split data on periods
    with open(filename, 'r') as f:
        all_split_data = [x.split('.') for x in f.readlines()]
    f.close()

    numYears = int((len(all_split_data) - firstline) / numSites)
    MonthlyIWR = np.zeros([12 * numYears, numSites])
    for i in range(numYears):
        for j in range(numSites):
            index = firstline + i * numSites + j
            all_split_data[index][0] = all_split_data[index][0].split()[2]
            MonthlyIWR[i * 12:(i + 1) * 12, j] = np.asfarray(all_split_data[index][0:12], float)

    np.savetxt('./CMIP_scenarios/' + scenario + '/MonthlyIWR.csv', MonthlyIWR, fmt='%d', delimiter=',')

