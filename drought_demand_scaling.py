import os
import pyDOE2

directories = os.listdir('./CMIP_curtailment')
scenarios = len(directories)

shortage_levels = [10, 20, 30]
no_users = [2, 5, 10]
curtailment = [20, 50, 100]
duration = [1, 2, 5]

sample = pyDOE2.fullfact([3, 3, 3, 3])