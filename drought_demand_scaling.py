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

monthly_iwr = np.loadtxt('./CMIP_scenarios/' + scenario + '/MonthlyIWR.csv', delimiter=',')
monthly_flows = np.loadtxt('./CMIP_scenarios/' + scenario + '/MonthlyFlows.csv', delimiter=',')

