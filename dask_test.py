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

sample_number_regex = re.compile(r'_S(\d+)_')
realization_number_regex = re.compile(r'_(\d+)(?:\.xdd)?$')

def file_manipulator(file_path):
    path = Path(file_path)
    logging.info('Parsing file ' + path)
    try:
        sample_number = int(sample_number_regex.search(path.stem).group(1))
        realization_number = int(realization_number_regex.search(path.stem).group(1))
    except (IndexError, AttributeError):
        logging.error(f"Unable to parse sample or realization number from file name: {path.stem}.")
        return False
    return sample_number, realization_number

L=client.map(file_manipulator, './scenarios/S1_1/*.xdd')
print(L)