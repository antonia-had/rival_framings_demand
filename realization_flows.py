import argparse
import numpy as np

numSites = 379

def realization_monthly_flow(i, j):
    realization = 'S' + str(i) + '_' + str(j)
    print('generating flows for ' + realization)
    file = open('../LHsamples_wider_100_AnnQonly/cm2015x_'+realization+'.xbm', 'r')
    all_split_data = [x.split('.') for x in file.readlines()]
    file.close()
    yearcount = 0
    flows = np.zeros([105, 12])
    for k in range(16, len(all_split_data)):
        row_data = []
        row_data.extend(all_split_data[k][0].split())
        if row_data[1] == '09163500':
            if int(row_data[0]) >= 1950:
                data_to_write = [row_data[2]] + all_split_data[k][1:12]
                flows[yearcount, :] = [int(n) for n in data_to_write]
                yearcount += 1
    np.savetxt('./scenarios/' + realization + '/' + realization + '_MonthlyFlows.csv', flows, fmt='%d', delimiter=',')
    annual_flows = np.sum(flows, axis=1)
    np.savetxt('./scenarios/' + realization + '/' + realization + '_AnnualFlows.csv', annual_flows, fmt='%d', delimiter=',')
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract monthly and annual flows per realization.')
    parser.add_argument('i', type=int,
                        help='scenario number')
    parser.add_argument('j', type=int,
                        help='realization number')
    args = parser.parse_args()
    print('executing realization '+str(args.i)+'_'+str(args.j))
    realization_monthly_flow(args.i, args.j)