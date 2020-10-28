# =============================================================================
# Define output extraction function
# =============================================================================
def getinfo(ID, scenario, path, design, sow):
    # Check if infofile doesn't already exist or if size is 0 (remove if wanting to overwrite old files)
    if path: #not (os.path.exists(path) and os.path.getsize(path) > 0):
        lines = []
        if design == 'CMIP_curtailment':
            with open(path, 'w') as f:
                # Read the first SOW separately so the year column is also collected
                with open('../' + design + '/' + scenario + '/cm2015/StateMod/cm2015B_S0.xdd', 'rt') as xdd_file:
                    for line in xdd_file:
                        data = line.split()
                        if data:
                            if data[0] == ID:
                                if data[3] != 'TOT':
                                    lines.append([data[2], data[4], data[17]])
                xdd_file.close()
                for j in range(1, sow):
                    yearcount = 0
                    try:
                        with open('../' + design + '/' + scenario + '/cm2015/StateMod/cm2015B_S' + str(j) + '.xdd',
                                  'rt') as xdd_file:
                            test = xdd_file.readline()
                            if test:
                                for line in xdd_file:
                                    data = line.split()
                                    if data:
                                        if data[0] == ID:
                                            if data[3] != 'TOT':
                                                lines[yearcount].extend([data[4], data[17]])
                                                yearcount += 1
                            else:
                                for i in range(len(lines)):
                                    lines[i].extend(['-999.', '-999.'])
                        xdd_file.close()
                    except IOError:
                        for i in range(len(lines)):
                            lines[i].extend(['-999.', '-999.'])
                for line in lines:
                    for item in line:
                        f.write("%s\t" % item)
                    f.write("\n")
            f.close()
        else:
            with open(path, 'w') as f:
                # Read the first SOW separately so the year column is also collected
                with open('../' + design + '/' + scenario + '/cm2015/StateMod/cm2015B.xdd', 'rt') as xdd_file:
                    for line in xdd_file:
                        data = line.split()
                        if data:
                            if data[0] == ID:
                                if data[3] != 'TOT':
                                    lines.append([data[2], data[4], data[17]])
                xdd_file.close()
                for line in lines:
                    for item in line:
                        f.write("%s\t" % item)
                    f.write("\n")
            f.close()