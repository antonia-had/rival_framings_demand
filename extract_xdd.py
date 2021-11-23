from pathlib import Path
import logging
import re
import io
import numpy as np
import pandas as pd
import argparse


sample_number_regex = re.compile('S(\d+)_')
realization_number_regex = re.compile(r'_(\d+)_')
rule_number_regex = re.compile(r'_(\d+)(?:\.xdd)?$')

expected_column_sizes = np.asarray([
            11, 12, 4, 4, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 12, 11
        ])
ids_of_interest = np.genfromtxt('ids.txt', dtype='str').tolist()
expected_line_size = expected_column_sizes.sum() + len(expected_column_sizes)
expected_column_count = 35
id_column = 1
year_column = 2
month_column = 3
demand_column = 4
shortage_column = 17
outflow_column = 31
control_location_column = 33
id_column_name = 'structure_id'
year_column_name = 'year'
month_column_name = 'month'
demand_column_name = 'demand'
shortage_column_name = 'shortage'
outflow_column_name = 'river_outflow'
control_location_column_name = 'control_location'
id_column_type = object
year_column_type = np.uint16
month_column_type = object
demand_column_type = np.uint32
shortage_column_type = np.uint32
outflow_column_type = np.uint32
control_location_column_type = object
sample_column_name = 'sample'
sample_column_type = np.uint16
realization_column_name = 'realization'
rule_column_name = 'demand rule'
realization_column_type = np.uint8
rule_column_type = np.uint16
outputs_path = '/expanse/lustre/scratch/ah986/temp_project/rival_framings_demand/xdd_parquet'
#'/ocean/projects/ees200007p/ah986/rival_framings_demand/xdd_parquet'
# #'/oasis/scratch/comet/ah986/temp_project/rival_framings_demand/xdd_parquet'


def xxd_to_parquet(file_path):
    path = Path(file_path)
    try:
        sample_number = int(sample_number_regex.search(path.stem).group(1))
        realization_number = int(realization_number_regex.search(path.stem).group(1))
        rule_number = int(rule_number_regex.search(path.stem).group(1))
    except (IndexError, AttributeError):
        logging.error(f"Unable to parse sample or realization number from file name: {path.stem}.")
        return False
    # stream will hold CSV of interesting data
    stream = io.StringIO()
    # read the file line by line
    with open(path, 'r') as file:
        for line in file:
            if line[expected_column_sizes[0] + 1:expected_column_sizes[1] + 1].strip() in ids_of_interest:
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
                                shortage_column,
                                outflow_column,
                                control_location_column
                            ]]
                        )
                    )
                    stream.write('\n')
    stream.seek(0)

    df = pd.read_csv(
        stream,
        header=None,
        names=[
            id_column_name,
            year_column_name,
            month_column_name,
            demand_column_name,
            shortage_column_name,
            outflow_column_name,
            control_location_column_name
        ],
        dtype={
            id_column_name: id_column_type,
            year_column_name: year_column_type,
            month_column_name: month_column_type,
            demand_column_name: demand_column_type,
            shortage_column_name: shortage_column_type,
            outflow_column_name: outflow_column_type,
            control_location_column_name: control_location_column_type
        }
    )

    stream.close()

    df[sample_column_name] = sample_column_type(sample_number)
    df[realization_column_name] = realization_column_type(realization_number)
    df[rule_column_name] = rule_column_type(rule_number)
    df.to_parquet(
        Path(f'{outputs_path}/S{sample_number}_{realization_number}/S{sample_number}_{realization_number}_{rule_number}.parquet'),
        engine='pyarrow',
        compression='gzip'
    )
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert .xdd to .parquet')
    parser.add_argument('file_path', type=str,
                        help='path to .xdd file')
    args = parser.parse_args()
    xxd_to_parquet(args.file_path)