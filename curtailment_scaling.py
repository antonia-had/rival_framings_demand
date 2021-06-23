import os
import pickle
from utils import *
from string import Template
import argparse

realizations = np.arange(1,11,1)

'''Read RSP template'''
T = open('./cm2015B_template.rsp', 'r')
template_RSP = Template(T.read())

def curtailment_scaling(i, j):
    scenario = 'S' + str(i) + '_' + str(j)
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
    for k in range(len(sample[:, 0])):
        # Check if realization run successfully first
        outputfilename = './scenarios/' + scenario + '/cm2015B_' + scenario + '_' + str(k) + '.xdd'
        if not os.path.isfile(outputfilename):
            print('generating ' + scenario + '_' + str(k))
            trigger_flow = trigger_flows[sample[k, 0]]
            users = users_per_threshold[sample[k, 1]]
            curtailment_per_user = list(curtailment_per_threshold[sample[k, 1]])
            general_curtailment = curtailment_levels[sample[k, 2]]

            annual_flows = np.loadtxt('./scenarios/' + scenario + '/' + scenario + '_AnnualFlows.csv')
            low_flows = annual_flows <= trigger_flow
            curtailment_years = list(np.arange(1909, 2014)[low_flows])

            writenewIWR(scenario, all_split_data, all_data, firstline_iwr, k, users,
                        curtailment_per_user, general_curtailment, curtailment_years)

            writenewDDM(scenario, all_data_DDM, firstline_ddm, CMIP_IWR, firstline_iwr, k,
                        users,curtailment_years)

            d = {'IWR': 'cm2015B_' + scenario + '_' + str(k) + '.iwr',
                 'DDM': 'cm2015B_' + scenario + '_' + str(k) + '.ddm',
                 'XBM': 'cm2015x_' + scenario + '.xbm'}
            new_rsp = template_RSP.safe_substitute(d)
            f1 = open('./scenarios/' + scenario + '/cm2015B_' + scenario + '_' + str(k) + '.rsp', 'w')
            f1.write(new_rsp)
            f1.close()
            print('running ' + scenario + '_' + str(k))
            # Run simulation
            os.chdir("/ocean/projects/ees200007p/ah986/rival_framings_demand/scenarios/{}".format(scenario))
            print(os.getcwd())
            os.system("./statemod cm2015B_{}_{} -simulate".format(scenario, k))
            os.chdir("/ocean/projects/ees200007p/ah986/rival_framings_demand")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract monthly and annual flows per realization.')
    parser.add_argument('i', type=int,
                        help='scenario number')
    parser.add_argument('j', type=int,
                        help='realization number')
    args = parser.parse_args()
    curtailment_scaling(args.i, args.j)