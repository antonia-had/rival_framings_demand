#!/bin/bash
#SBATCH --job-name="curtailment_scaling"
#SBATCH --output="curtailment_scaling.out"
#SBATCH --nodes=10
#SBATCH --ntasks-per-node=16
#SBATCH --export=ALL
#SBATCH -t 1:00:00            # set max wallclock time

module load python/3.6.9
source /home/fs02/pmr82_0001/ah986/envs/rival_framings/bin/activate
mpirun python3 curtailment_scaling.py
