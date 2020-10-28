import math
import os
import glob
import numpy as np

design = 'CMIP_scenarios'
directories = glob.glob('../' + design + '/CMIP*_*')
directories = [x[-9:] for x in directories]
scenarios = 209
realizations = 1
no_months = 64*12
idx = np.arange(2, realizations*2+2, 2)
all_IDs = np.genfromtxt('../structures_files/metrics_structures.txt', dtype='str').tolist()

for i in range(len(all_IDs)):
    print(i)
    ID = all_IDs[i]
    summary_file_path = '../' + design + '/Infofiles/' + ID + '/' + ID + '_all.txt'
    # if os.path.exists(summary_file_path):
    #     SYN_short = np.loadtxt(summary_file_path)
    # else:
    SYN_short = np.zeros([no_months, scenarios*realizations])
    for j in range(scenarios*realizations):
        infofile_path = '../' + design + '/Infofiles/' + ID + '/' + ID + '_info_' + directories[j] + '.txt'
        data = np.loadtxt(infofile_path)
        try:
            SYN_short[:, j * realizations:j * realizations + realizations] = data[:, idx]
        except IndexError:
            print('IndexError ' + ID + '_info_' + directories[j])
    np.savetxt(summary_file_path, SYN_short)