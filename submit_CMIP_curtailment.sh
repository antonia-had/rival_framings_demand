#!/bin/bash
#SBATCH --job-name="statemod"
#SBATCH --output="statemodruns.out"
#SBATCH --nodes=6
#SBATCH --ntasks-per-node=16
#SBATCH --export=ALL
#SBATCH -t 10:00:00            # set max wallclock time

module load python/3.6.9
source /home/fs02/pmr82_0001/ah986/envs/rival_framings/bin/activate
mpirun python3 submit_CMIP_curtailment.py

