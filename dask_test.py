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

import time

def increment(x):
    time.sleep(0.5)
    print(x*2)
    return

client.map(increment, range(100))