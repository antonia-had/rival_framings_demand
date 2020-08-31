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


def writenewIWR(directory, filename, sample, users, curtailment_per_user, general_curtailment, curtailment_years):

    firstLine = int(search_string_in_file('./CMIP_scenarios/' + directory + '/cm2015/StateMod/'+filename, '#>EndHeader')[0]) + 4
    # split data on periods
    with open('./CMIP_scenarios/' + directory + '/cm2015/StateMod/'+filename, 'r') as f:
        all_split_data = [x.split('.') for x in f.readlines()]
    f.close()

    # get unsplit data to rewrite firstLine # of rows
    with open('./CMIP_scenarios/' + directory + '/cm2015/StateMod/'+filename, 'r') as f:
        all_data = [x for x in f.readlines()]
    f.close()

    # replace former iwr demands with new
    new_data = []
    for i in range(len(all_split_data) - firstLine):
        row_data = []
        # split first 3 columns of row on space and find 1st month's flow
        row_data.extend(all_split_data[i + firstLine][0].split())
        # check if year is a curtailment year and if user is to be curtailed
        if row_data[0] in curtailment_years and row_data[1] in users:
            index = np.where(users==row_data[1])
            remaining_demand = 1-(curtailment_per_user[index]*(100-general_curtailment)/100)
            #scale first month
            row_data[2] = str(int(float(row_data[2])*remaining_demand))
            #scale other months
            for j in range(len(all_split_data[i + firstLine]) - 2):
                row_data.append(str(int(float(all_split_data[i + firstLine][j + 1]) * remaining_demand)))
        # append row of adjusted data
        new_data.append(row_data)

    f = open('./CMIP_curtailment/' + directory + '/cm2015/StateMod/' + filename[0:-4] + '_S' + str(sample) + filename[-4::], 'w')
    # write firstLine # of rows as in initial file
    for i in range(firstLine):
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
    print('./CMIP_curtailment/' + directory + '/cm2015/StateMod/' + filename[0:-4] + '_S' + str(sample) + filename[-4::])

    return None