#!/bin/bash

#SBATCH --nodes=5
#SBATCH --ntasks-per-node=66
#SBATCH -p normal
#SBATCH -t 3:00:00
#SBATCH --export=ALL
#SBATCH --mail-user=ah986@cornell.edu
#SBATCH --mail-type=ALL

source /home/fs02/pmr82_0001/ah986/rival_framings/bin/activate
mpirun python3 data_extraction.py