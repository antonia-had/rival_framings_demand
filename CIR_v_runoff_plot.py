import os
import numpy as np
import matplotlib.pyplot as plt
from utils import search_string_in_file

numSites = 379


def realization_mean_IWR(filename, firstline=463, h=0, sample=None):
    '''Get historical irrigation and runoff values'''
    with open(filename, 'r') as f:
        all_split_data = [x.split('.') for x in f.readlines()]
    f.close()
    numYears = int((len(all_split_data) - firstline) / numSites)
    # get monthly demands
    MonthlyIWR = np.zeros([12 * numYears, numSites])
    for i in range(numYears):
        for j in range(numSites):
            index = firstline + i * numSites + j
            all_split_data[index][0] = all_split_data[index][0].split()[2]
            MonthlyIWR[i * 12:(i + 1) * 12, j] = np.asfarray(all_split_data[index][0:12], float)
    if h == 0:
        np.savetxt(filename[:-28] + '/MonthlyIWR.csv', MonthlyIWR, fmt='%d', delimiter=',')
    if h == 1:
        np.savetxt('./hist_files/MonthlyIWR.csv', MonthlyIWR, fmt='%d', delimiter=',')
    if h == 2:
        np.savetxt(filename[:29] + '/MonthlyIWR_S{}.csv'.format(sample), MonthlyIWR, fmt='%d', delimiter=',')
    # calculate annual demands
    AnnualIWR = np.zeros([numYears, numSites])
    for i in range(numYears):
        AnnualIWR[i, :] = np.sum(MonthlyIWR[i * 12:(i + 1) * 12], 0)
    mean_IWR = np.mean(np.sum(AnnualIWR, axis=1))
    return mean_IWR


def realization_mean_flow(filename, h=0):
    file = open(filename, 'r')
    all_split_data = [x.split('.') for x in file.readlines()]
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
    if h == 0:
        np.savetxt(filename[:-28] + '/MonthlyFlows.csv', flows, fmt='%d', delimiter=',')
    if h == 1:
        np.savetxt('./hist_files/MonthlyFlows.csv', flows, fmt='%d', delimiter=',')
    mean_flow = np.mean(np.sum(flows, axis=1))
    return mean_flow


'''Get values from history'''
hist_IWR = realization_mean_IWR('./hist_files/cm2015B.iwr', 16002, h=1)
hist_flow = realization_mean_flow('./hist_files/cm2015x.xbm', h=1)

'''Get values from every CMIP scenario'''
if os.path.exists("anomalies_CMIP.txt"):
    anomalies = np.loadtxt('anomalies_CMIP.txt')
else:
    directories = os.listdir('./CMIP_scenarios')
    scenarios = len(directories)

    anomalies = np.zeros([scenarios, 2])

    '''Loop through every scenario and get total irrigation demand and runoff'''
    for i in range(scenarios):
        directory = directories[i]
        filename = './CMIP_scenarios/' + directory + '/cm2015/StateMod/cm2015'
        firstline = int(search_string_in_file(filename + 'B.iwr', '#>EndHeader')[0]) + 4
        anomalies[i, 0] = realization_mean_IWR(filename + 'B.iwr', firstline, h=0)
        anomalies[i, 1] = realization_mean_flow(filename + 'x.xbm', h=0)
    np.savetxt('anomalies_CMIP.txt', anomalies)

'''Get values from every CMIP curtailment scenario'''
if os.path.exists("anomalies_CMIP_curtailment.txt"):
    anomalies_curtailment = np.loadtxt('anomalies_CMIP_curtailment.txt')
else:
    directories = os.listdir('./CMIP_curtailment')
    scenarios = len(directories)
    sow = 27

    anomalies_curtailment = np.zeros([scenarios * sow, 2])

    '''Loop through every scenario and every demand SOW and get total irrigation demand and runoff'''
    for i in range(scenarios):
        directory = directories[i]
        filename = './CMIP_curtailment/' + directory + '/cm2015/StateMod/cm2015'
        print(filename)
        anomalies_curtailment[i * 10:i * 10 + 10, 1] = realization_mean_flow(filename + 'x.xbm', h=2)
        for j in range(sow):
            firstline = int(search_string_in_file(filename + 'B_S{}.iwr'.format(j), '#>EndHeader')[0]) + 4
            anomalies_curtailment[i * 10 + j, 0] = realization_mean_IWR(filename + 'B_S{}.iwr'.format(j), firstline, h=2, sample=j)
            print(anomalies_curtailment[i * 10 + j, 0])
    np.savetxt('anomalies_CMIP_curtailment.txt', anomalies_curtailment)

'''Assign rank to every scenario including history'''
# CMIP scenarios
anomalies = np.vstack([anomalies, [hist_IWR, hist_flow]])
anomalies_norm = np.zeros_like(anomalies)
# CMIP scenarios curtailed
anomalies_curtailment = np.vstack([anomalies_curtailment])
anomalies_curtailment_norm = np.zeros_like(anomalies_curtailment)
for i in range(2):
    maxvalue = max(anomalies_curtailment[:, i].max(), anomalies[:, i].max())
    minvalue = min(anomalies_curtailment[:, i].min(), anomalies[:, i].min())
    anomalies_curtailment_norm[:, i] = (anomalies_curtailment[:, i] - minvalue) / (maxvalue-minvalue)
    anomalies_norm[:, i] = (anomalies[:, i] - minvalue) / (maxvalue-minvalue)

fig,axes = plt.subplots(2,1, dpi=300)
# Plot original CMIP anomalies
ax = axes[0]
ax.scatter(anomalies_norm[:, 0], anomalies_norm[:, 1], s=10)
ax.scatter(anomalies_norm[-1, 0], anomalies_norm[-1, 1], s=20, c='red')
ax.set_ylabel('Normalized runoff', fontsize=12)
ax.set_title('Original CMIP scenarios', fontsize=14)
ax.set_xticks([])
ax.set_xlim(0, 1.05)
ax.set_ylim(0, 1.05)
# Plot curtailed CMIP anomalies
ax = axes[1]
ax.scatter(anomalies_curtailment_norm[:, 0], anomalies_curtailment_norm[:, 1], s=10)
ax.scatter(anomalies_curtailment_norm[-1, 0], anomalies_curtailment_norm[-1, 1], s=20, c='red')
ax.set_xlabel('Normalized irrigation demand', fontsize=12)
ax.set_ylabel('Normalized runoff', fontsize=12)
ax.set_title('CMIP scenarios with curtailment', fontsize=14)
ax.set_xlim(0, 1.05)
ax.set_ylim(0, 1.05)
fig.suptitle('Runoff anomaly vs. irrigation demand anomaly', fontsize=16)

plt.savefig('IWR_v_runoff.png')
