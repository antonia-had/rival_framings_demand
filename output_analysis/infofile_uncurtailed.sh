#!/bin/bash
#SBATCH --job-name="infofiles"
#SBATCH --output="infofiles.out"
#SBATCH --hint=nomultithread
#SBATCH --nodes=10
#SBATCH --ntasks-per-node=16
#SBATCH --export=ALL
#SBATCH -t 20:00:00            # set max wallclock time
#SBATCH --mail-user=ah986@cornell.edu
#SBATCH --mail-type=ALL

module load python/3.6.9
source /home/fs02/pmr82_0001/ah986/envs/rival_framings/bin/activate
mpirun python3 infofile_uncurtailed.py CMIP_curtailment
