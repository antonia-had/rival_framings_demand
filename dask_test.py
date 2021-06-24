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

import numpy as np

def multiplier(x):
    array = np.arange(x*2)
    np.savetxt(str(x)+'.txt', array)
    return

L=client.map(multiplier, range(100))
