import os
import pickle
from utils import *
from string import Template
import math
from realization_flows import realization_monthly_flow

# sows = np.arange(1, 101, 1)
sows = np.arange(1, 2, 1)
realizations = np.arange(1,2,1)
all_scenarios = ['S'+str(i)+'_'+str(j) for i in sows for j in realizations]

'''Read RSP template'''
T = open('./cm2015B_template.rsp', 'r')
template_RSP = Template(T.read())

# Begin parallel simulation
comm = MPI.COMM_WORLD

# Get the number of processors and the rank of processors
rank = comm.rank
nprocs = comm.size

# Determine the chunk which each processor will need to do
count = int(math.floor(len(all_scenarios) / nprocs))
remainder = len(all_scenarios) % nprocs

# Use the processor rank to determine the chunk of work each processor will do
if rank < remainder:
    start = rank * (count + 1)
    stop = start + count + 1
else:
    start = remainder * (count + 1) + (rank - remainder) * count
    stop = start + count

for scenario in all_scenarios[start:stop]:
    '''Get data from scenario IWR'''
    firstline_iwr = 463#int(search_string_in_file('../LHsamples_wider_100_AnnQonly/cm2015B_'+scenario+'.iwr', '#>EndHeader')[0]) + 4
    CMIP_IWR = []
    all_data = []
    all_split_data = []
    with open('../LHsamples_wider_100_AnnQonly/cm2015B_'+scenario+'.iwr', 'r') as f:
        for x in f.readlines():
            CMIP_IWR.append(x.split())
            all_data.append(x)
            all_split_data.append(x.split('.'))
    CMIP_IWR = CMIP_IWR[firstline_iwr:]

    '''Get data from scenario DDM'''
    firstline_ddm = 779#int(search_string_in_file('../LHsamples_wider_100_AnnQonly/cm2015B_'+scenario+'.ddm','#>EndHeader')[0]) + 4

    with open('../LHsamples_wider_100_AnnQonly/cm2015B_'+scenario+'.ddm', 'r') as f:
        all_data_DDM = [x for x in f.readlines()]

    # Apply each demand sample to every generator scenario
    sample = np.loadtxt('factorial_sample.txt')
    curtailment_levels = np.loadtxt('curtailment_levels.txt')
    trigger_flows = np.loadtxt('trigger_flows.txt', dtype=int)
    with open("users_per_threshold.txt", "rb") as fp:
        users_per_threshold = pickle.load(fp)
    with open("curtailment_per_threshold.txt", "rb") as fp:
        curtailment_per_threshold = pickle.load(fp)
    for i in range(len(sample[:, 0])):
        # Check if realization run successfully first
        outputfilename = './scenarios/' + scenario + '/cm2015B_' + scenario + '_' + str(i) + '.xdd'
        if not os.path.isfile(outputfilename):
            print('generating ' + scenario + '_' + str(i))
            trigger_flow = trigger_flows[sample[i, 0]]
            users = users_per_threshold[sample[i, 1]]
            curtailment_per_user = list(curtailment_per_threshold[sample[i, 1]])
            general_curtailment = curtailment_levels[sample[i, 2]]

            annual_flows = np.loadtxt('./scenarios/' + scenario + '/' + scenario + '_AnnualFlows.csv')
            low_flows = annual_flows <= trigger_flow
            curtailment_years = list(np.arange(1909, 2014)[low_flows])

            writenewIWR(scenario, all_split_data, all_data, firstline_iwr, i, users,
                        curtailment_per_user, general_curtailment, curtailment_years)

            writenewDDM(scenario, all_data_DDM, firstline_ddm, CMIP_IWR, firstline_iwr, i, users,curtailment_years)

            d = {'IWR': 'cm2015B_' + scenario + '_' + str(i) + '.iwr',
                 'DDM': 'cm2015B_' + scenario + '_' + str(i) + '.ddm',
                 'XBM': 'cm2015x_' + scenario + '.xbm'}
            S1 = template_RSP.safe_substitute(d)
            f1 = open('./scenarios/' + scenario + '/cm2015B_' + scenario + '_' + str(i) + '.rsp', 'w')
            f1.write(S1)
            f1.close()
            print('running ' + scenario + '_' + str(i))
            # Run simulation
            os.chdir("/ocean/projects/ees200007p/ah986/rival_framings_demand/scenarios/{}".format(scenario))
            print(os.getcwd())
            os.system("./statemod cm2015B_{}_{} -simulate".format(scenario, i))
            os.chdir("/ocean/projects/ees200007p/ah986/rival_framings_demand")
