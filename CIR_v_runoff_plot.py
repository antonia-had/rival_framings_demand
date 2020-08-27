import os
import numpy as np

directories = os.listdir('./CMIP_scenarios')
scenarios = len(directories)

anomalies = np.zeros([2, scenarios])

'''Get historical irrigation and runoff values'''
with open('../Statemod_files/cm2015B.iwr','r') as f:
    hist_IWR = [x.split() for x in f.readlines()[463:]]
f.close()

'''Loop through every scenario and get total irrigation demand and runoff'''
for i in range(len(scenarios)):
    with open('../'+design+'/Experiment_files/cm2015B_S'+ str(k+1) + '_' + str(l+1) + 'a.iwr') as f:
        sample_IWR = [x.split() for x in f.readlines()[463:]]
    f.close()