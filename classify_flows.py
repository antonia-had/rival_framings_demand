import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


generated_flows_wider = np.load('LHsamples_wider_100_AnnQonly_flows.npy')
samples = pd.read_csv('LHsamples_wider_100_AnnQonly.txt', header=0, delim_whitespace=True)

CMIP_flows = np.load('CMIP_SOWs_flows.npy')
historic_flows = np.load('historic_flows.npy')
stationary_flows = np.load('stationarysynthetic_flows.npy')

data = [generated_flows_wider, CMIP_flows, stationary_flows]
data_metric = [x*1233.4818 for x in data]
data_mins = [np.min(np.min(dataset, axis=0), axis=0) for dataset in data_metric]
data_maxs = [np.max(np.max(dataset, axis=0), axis=0) for dataset in data_metric]

historic_mins = np.min(historic_flows*1233.4818, axis=0)
historic_maxs = np.max(historic_flows*1233.4818, axis=0)


colors = ['#9597a3', '#D0CD94', '#305252', '#DD7373']
labels = ['All encompassing', 'CMIP5 & CMIP3', 'Stationary synthetic', 'Historic']

fig = plt.figure(figsize=(12, 9))
ax1 = fig.add_subplot(111)
for i in range(len(data)):
    ax1.fill_between(range(12), data_mins[i],
                     data_maxs[i], color=colors[i],
                     label=labels[i], alpha=0.8)
ax1.fill_between(range(12), historic_mins,
                 historic_maxs, color=colors[3],
                 label=labels[3], alpha=0.8)
ax1.set_yscale("log")
ax1.set_xlabel('Month', fontsize=16)
ax1.set_ylabel('Flow at Last Node ($m^3$)', fontsize=16)
ax1.set_xlim([0, 11])
ax1.tick_params(axis='both', labelsize=14)
ax1.set_xticks(range(12))
ax1.set_xticklabels(['O','N','D','J','F','M','A','M','J','J','A','S'])
handles, labels = plt.gca().get_legend_handles_labels()
labels, ids = np.unique(labels, return_index=True)
handles = [handles[i] for i in ids]
fig.subplots_adjust(bottom=0.2)
fig.legend(handles, labels, fontsize=16, loc='lower center', ncol=4)
ax1.set_title('Streamflow across experiments',fontsize=18)
plt.savefig('experiment_ranges.png')
plt.close()

fig = plt.figure(figsize=(12, 9))
ax2 = fig.add_subplot(111)
generated_flows_flat = generated_flows_wider.reshape(1000*105, 12)*1233.4818
for j in range(len(generated_flows_flat)):
    #first check if flows lay within historical range
    zipped_list = list(zip(generated_flows_flat[j, :], historic_mins, historic_maxs))
    boolean_list = [True if monthly_value[0] >= monthly_value[1] and monthly_value[0] <= monthly_value[2]\
                    else False for monthly_value in zipped_list]
    if all(boolean_list):
        color = '#DD7373'
        ax2.plot(range(12), generated_flows_flat[j, :], color=color, alpha=0.1)
    else:
        #check if flows lay within experiment ranges, loop through datasets in reverse order
        for k in range(2, -1, -1):
            zipped_list = list(zip(generated_flows_flat[j, :], data_mins[k], data_maxs[k]))
            boolean_list = [True if monthly_value[0] >= monthly_value[1] and monthly_value[0] <= monthly_value[2] \
                                else False for monthly_value in zipped_list]
            if all(boolean_list):
                color = colors[k]
                ax2.plot(range(12), generated_flows_flat[j, :], color=color, alpha=0.1)
                break

#ax.plot(range(12), historic_data[93,:]*1233.4818, color='#AA1209', linewidth = 2, label='Water Year 2002')
ax2.set_yscale("log")
ax2.set_xlabel('Month', fontsize=16)
ax2.set_ylabel('Flow at Last Node ($m^3$)', fontsize=16)
ax2.set_xlim([0, 11])
ax2.tick_params(axis='both', labelsize=14)
ax2.set_xticks(range(12))
ax2.set_xticklabels(['O','N','D','J','F','M','A','M','J','J','A','S'])
plt.savefig('flows_classification.png')
plt.close()

fig = plt.figure(figsize=(12, 9))
ax2 = fig.add_subplot(111)
generated_flows_flat = generated_flows_wider.reshape(1000*105, 12)*1233.4818
for j in range(len(generated_flows_flat)):
    ax2.plot(range(12), generated_flows_flat[j, :], color='#9597a3', alpha=0.1)

#ax.plot(range(12), historic_data[93,:]*1233.4818, color='#AA1209', linewidth = 2, label='Water Year 2002')
ax2.set_yscale("log")
ax2.set_xlabel('Month', fontsize=16)
ax2.set_ylabel('Flow at Last Node ($m^3$)', fontsize=16)
ax2.set_xlim([0, 11])
ax2.tick_params(axis='both', labelsize=14)
ax2.set_xticks(range(12))
ax2.set_xticklabels(['O','N','D','J','F','M','A','M','J','J','A','S'])
plt.savefig('all_flows.png')
plt.close()