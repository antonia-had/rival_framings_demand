#!/bin/bash
#SBATCH --job-name="shortage_curves"
#SBATCH --output="shortage_curves.out"
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=6
#SBATCH --export=ALL
#SBATCH -t 1:00:00            # set max wallclock time
#SBATCH --mail-user=ah986@cornell.edu
#SBATCH --mail-type=ALL

module load python/3.6.9
source /home/fs02/pmr82_0001/ah986/envs/rival_framings/bin/activate
mpirun python3 shortage_duration_curves.py CMIP_curtailment
