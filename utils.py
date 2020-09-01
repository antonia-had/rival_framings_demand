import numpy as np

def search_string_in_file(file_name, string_to_search):
    """Search for the given string in file and return the line numbers containing that string"""
    line_number = 0
    list_of_results = []
    # Open the file in read only mode
    with open(file_name, 'r') as read_obj:
        # Read all lines in the file one by one
        for line in read_obj:
            # For each line, check if line contains the string
            line_number += 1
            if string_to_search in line:
                # If yes, then add the line number & line as a tuple in the list
                list_of_results.append((line_number))
    # Return list of tuples containing line numbers and lines where string is found
    return list_of_results


def writenewIWR(scenario, all_split_data, all_data, firstline_iwr, sow, users,
                    curtailment_per_user, general_curtailment, curtailment_years):
    # replace former iwr demands with new
    new_data = []
    for i in range(len(all_split_data) - firstline_iwr):
        row_data = []
        # split first 3 columns of row on space and find 1st month's flow
        row_data.extend(all_split_data[i + firstline_iwr][0].split())
        # check if year is a curtailment year and if user is to be curtailed
        if int(row_data[0]) in curtailment_years and row_data[1] in users:
            index = np.where(users==row_data[1])[0][0]
            remaining_demand = 1-(curtailment_per_user[index]*(100-general_curtailment)/100)
            #scale first month
            row_data[2] = str(int(float(row_data[2])*remaining_demand))
            #scale other months
            for j in range(len(all_split_data[i + firstline_iwr]) - 2):
                row_data.append(str(int(float(all_split_data[i + firstline_iwr][j + 1]) * remaining_demand)))
        else:
            for j in range(len(all_split_data[i + firstline_iwr]) - 2):
                row_data.append(str(int(float(all_split_data[i + firstline_iwr][j + 1]))))
        # append row of adjusted data
        new_data.append(row_data)

    f = open('./CMIP_curtailment/' + scenario + '/cm2015/StateMod/cm2015B_S' + str(sow) + '.iwr', 'w')
    # write firstLine # of rows as in initial file
    for i in range(firstline_iwr):
        f.write(all_data[i])
    for i in range(len(new_data)):
        # write year, ID and first month of adjusted data
        f.write(new_data[i][0] + ' ' + new_data[i][1] + (19 - len(new_data[i][1]) - len(new_data[i][2])) * ' ' +
                new_data[i][2] + '.')
        # write all but last month of adjusted data
        for j in range(len(new_data[i]) - 4):
            f.write((7 - len(new_data[i][j + 3])) * ' ' + new_data[i][j + 3] + '.')
        # write last month of adjusted data
        f.write((9 - len(new_data[i][-1])) * ' ' + new_data[i][-1] + '.' + '\n')
    f.close()
    return None


def writenewDDM(scenario, all_data_DDM, all_split_data_DDM, firstline_ddm, CMIP_IWR,
                firstline_iwr, sow, users, curtailment_years):

    with open('./CMIP_curtailment/' + scenario + '/cm2015/StateMod/cm2015B_S'+ str(sow) +'.iwr') as f:
        sample_IWR = [x.split() for x in f.readlines()[firstline_iwr:]]
    f.close()

    new_data = []
    irrigation_encounters = np.zeros(len(users))

    for i in range(len(all_split_data_DDM) - firstline_ddm):
        # To store the change between historical and sample irrigation demand (12 months + Total)
        change = np.zeros(13)
        # Split first 3 columns of row on space
        # This is because the first month is lumped together with the year and the ID when spliting on periods
        row_data = all_split_data_DDM[i + firstline_ddm]
        # If the structure is not in the ones we care about then do nothing
        if int(row_data[0]) in curtailment_years and row_data[1] in users:
            index = np.where(users == row_data[1])[0][0]
            line_in_iwr = int(irrigation_encounters[index] * len(users) + index)
            irrigation_encounters[index] = +1
            for m in range(len(change)):
                change[m] = float(sample_IWR[line_in_iwr][2 + m]) - float(CMIP_IWR[line_in_iwr][2 + m])
                row_data[m+2] = str(int(float(row_data[m+2]) + change[m]))
                # append row of adjusted data
        new_data.append(row_data)
        # write new data to file
    f = open('./CMIP_curtailment/' + scenario + '/cm2015/StateMod/cm2015B_S'+ str(sow) +'.ddm', 'w')
    # write firstLine # of rows as in initial file
    for i in range(firstline_ddm):
        f.write(all_data_DDM[i])
    for i in range(len(new_data)):
        # write year, ID and first month of adjusted data
        f.write(new_data[i][0] + ' ' + new_data[i][1] + (20 - len(new_data[i][1]) - len(new_data[i][2])) * ' ' +
                new_data[i][2])
        # write all but last month of adjusted data
        for j in range(len(new_data[i]) - 4):
            f.write((8 - len(new_data[i][j + 3])) * ' ' + new_data[i][j + 3])
            # write last month of adjusted data
        f.write((9 - len(new_data[i][-1])) * ' ' + new_data[i][-1] + '\n')
    f.close()

    return None