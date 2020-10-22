import math
import os
import numpy as np

design = '../LHsamples_original_1000'
samples = 10000
realizations = 10
no_months = 105*12
idx = np.arange(2, realizations*2+2, 2)
all_IDs = ['3600687', '7000550', '7200799', '7200645', '3704614', '7202003']#np.genfromtxt('../structures_files/metrics_structures.txt', dtype='str').tolist()

for i in range(len(all_IDs)):
    ID = all_IDs[i]
    summary_file_path = '../' + design + '/Infofiles/' + ID + '/' + ID + '_all.txt'
    if os.path.exists(summary_file_path):
        SYN_short = np.loadtxt(summary_file_path)
    else:
        SYN_short = np.zeros([no_months, samples])
        for j in range(int(samples/realizations)):
            infofile_path = '../' + design + '/Infofiles/' + ID + '/' + ID + '_info_' + str(j+1) + '.txt'
            data = np.loadtxt(infofile_path)
            try:
                SYN_short[:, j * realizations:j * realizations + realizations] = data[:, idx]
            except IndexError:
                print('IndexError ' + ID + '_info_' + str(j+1))
        np.savetxt(summary_file_path, SYN_short)

# for i in range(len(all_IDs)):
#     ID = all_IDs[i]
#     summary_file_path = '../' + design + '/Infofiles/' + ID + '/' + ID + '_all.txt'
#     if os.path.exists(summary_file_path):
#         SYN_short = np.loadtxt(summary_file_path)
#     else:
#         SYN_short = np.zeros([no_months, samples])
#         for j in range(int(samples/realizations)):
#             infofile_path = '../' + design + '/Infofiles/' + ID + '/' + ID + '_info_' + directories[j] + '.txt'
#             data = np.loadtxt(infofile_path)
#             try:
#                 SYN_short[:, j * realizations:j * realizations + realizations] = data[:, idx]
#             except IndexError:
#                 print('IndexError ' + ID + '_info_' + directories[j])
#         np.savetxt(summary_file_path, SYN_short)