#!/bin/bash
#SBATCH --job-name="15mileinfo"
#SBATCH --hint=nomultithread
#SBATCH --nodes=2             # specify number of nodes
#SBATCH --ntasks-per-node=16  # specify number of core per node
#SBATCH --export=ALL
#SBATCH -t 1:00:00            # set max wallclock time
#SBATCH --job-name="streamflow" # name your job 
#SBATCH --output="streamflow.out"

module load python/3.6.9
source /home/fs02/pmr82_0001/ah986/envs/rival_framings/bin/activate
mpirun python3 15mile_streamflow.py LHsamples_original_1000