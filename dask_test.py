from dask_jobqueue import SLURMCluster
from distributed import Client

cluster = SLURMCluster(cores=24,
                       processes=1,
                       memory="16GB",
                       walltime="0:30:00",
                       queue="compute")
cluster.scale(2)
print(cluster.job_script())
client = Client(cluster)

from pathlib import Path
import logging
import re
import io
import numpy as np

sample_number_regex = re.compile(r'_S(\d+)_')
realization_number_regex = re.compile(r'_(\d+)(?:\.xdd)?$')
expected_column_sizes = np.asarray([
            11, 12, 4, 4, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 12, 11
        ])
ids_of_interest = np.genfromtxt('ids.txt', dtype='str').tolist()
expected_line_size = expected_column_sizes.sum() + len(expected_column_sizes)
expected_column_count = 35
month_column = 3
id_column = 0
year_column = 2
demand_column = 4
shortage_column = 17

def file_manipulator(file_path):
    path = Path(file_path)
    logging.info('Parsing file ' + path)
    try:
        sample_number = int(sample_number_regex.search(path.stem).group(1))
        realization_number = int(realization_number_regex.search(path.stem).group(1))
    except (IndexError, AttributeError):
        logging.error(f"Unable to parse sample or realization number from file name: {path.stem}.")
        return False
    # stream will hold CSV of interesting data
    stream = io.StringIO()
    # read the file line by line
    with open(path, 'r') as file:
        for line in file:
            # note here that we make two simplifying assumptions:
            #   - all structure ids of interest start with a digit
            #   - only lines of data start with a digit
            if line[0].isdigit() and line[0:expected_column_sizes[0] + 1].strip() in ids_of_interest:
                if len(line) != expected_line_size:
                    # unexpected line length; you need to double check the expected column sizes
                    logging.error(
                        f"Unexpected line length: {len(line)} instead of {expected_line_size}:\n{line}"
                    )
                    return False
                # split data by character counts
                data = []
                position = 0
                for count in expected_column_sizes:
                    data.append(line[position:position + count].strip())
                    # account for single space between columns
                    position += count + 1
                if len(data) != expected_column_count:
                    # unexpected number of columns; you need to double check your data and settings
                    logging.error(
                        f"Unexpected column count: {len(data)} instead of {expected_column_count}:\n{line}"
                    )
                    return False
                # only keep non-total rows
                if not data[month_column].casefold().startswith('tot'):
                    stream.write(
                        ','.join(
                            [data[i] for i in [
                                id_column,
                                year_column,
                                month_column,
                                demand_column,
                                shortage_column
                            ]]
                        )
                    )
                    stream.write('\n')
    stream.seek(0)
    return

L=client.map(file_manipulator, './scenarios/S1_1/*.xdd')
