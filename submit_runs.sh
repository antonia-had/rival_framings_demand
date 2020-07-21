#!/bin/bash
#SBATCH --nodes=3             # specify number of nodes
#SBATCH --ntasks-per-node=16  # specify number of core per node
#SBATCH --export=ALL
#SBATCH -t 1:00:00            # set max wallclock time
#SBATCH --job-name="statemod" # name your job
#SBATCH --output="statemodruns.out"
#SBATCH --mail-user=ah986@cornell.edu
#SBATCH --mail-type=ALL

module load python
module load mpi4py
ibrun python3 submit_CMIP_runs.py