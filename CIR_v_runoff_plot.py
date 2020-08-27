import os
import numpy as np
import matplotlib.pyplot as plt

numSites = 379
firstline = 463

def realization_mean_IWR(filename):
    '''Get historical irrigation and runoff values'''
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
    # calculate annual flows
    AnnualIWR = np.zeros([numYears, numSites])
    for i in range(numYears):
        AnnualIWR[i, :] = np.sum(MonthlyIWR[i * 12:(i + 1) * 12], 0)
    mean_IWR = np.mean(np.sum(AnnualIWR, axis=1))
    return mean_IWR

def realization_mean_flow(filename):
    file = open(filename,'r')
    all_split_data = [x.split('.') for x in file.readlines()]
    yearcount = 0
    flows = np.zeros([105, 12])
    for i in range(16, len(all_split_data)):
        row_data = []
        row_data.extend(all_split_data[i][0].split())
        if row_data[1] == '09163500':
            data_to_write = [row_data[2]] + all_split_data[i][1:12]
            flows[yearcount, :] = [int(n) for n in data_to_write]
            yearcount += 1
    mean_flow = np.mean(np.sum(flows, axis=1))
    return mean_flow

'''Get values from history'''
hist_IWR = realization_mean_IWR('./hist_files/cm2015B.iwr')
hist_flow = realization_mean_flow('./hist_files/cm2015x.xbm')

'''Get values from every scenario'''
if os.path.exists("anomalies.txt"):
    anomalies = np.loadtxt('anomalies.txt')
else:
    directories = os.listdir('./CMIP_scenarios')
    scenarios = len(directories)

    anomalies = np.zeros([scenarios, 2])

    '''Loop through every scenario and get total irrigation demand and runoff'''
    for i in range(scenarios):
        directory = directories[i]
        print(directory)
        anomalies[i, 0] = realization_mean_IWR('./CMIP_scenarios/' + directory + '/cm2015/StateMod/cm2015B.iwr')
        anomalies[i, 1] = realization_mean_flow('./CMIP_scenarios/' + directory + '/cm2015/StateMod/cm2015x.xbm')
    np.savetxt('anomalies.txt', anomalies)

'''Assign rank to every scenario, including history'''
anomalies = np.vstack([anomalies, [hist_IWR,hist_flow]])
anomalies_norm = np.zeros_like(anomalies)
for i in range(2):
    anomalies_norm[:,i]=(anomalies[:,i] - anomalies[:,i].min()) / (np.ptp(anomalies[:,i]))

fig = plt.figure(figsize=(12, 9))
ax = plt.axes()
ax.scatter(anomalies_norm[:, 0], anomalies_norm[:, 1])
ax.set_xtitle('Irrigation demand')
ax.set_ytitle('Runoff')
plt.savefig('IWR_v_runoff.png')