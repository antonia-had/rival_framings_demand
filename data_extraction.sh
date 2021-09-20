#!/bin/bash

#SBATCH --nodes=2
#SBATCH --ntasks-per-node=80
#SBATCH -p normal
#SBATCH -t 0:30:00
#SBATCH --export=ALL


source /home/fs02/pmr82_0001/ah986/rival_framings/bin/activate
mpirun python3 data_extraction.py