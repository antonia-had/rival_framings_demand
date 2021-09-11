#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks=20
#SBATCH --cpus-per-task=1
#SBATCH -p normal
#SBATCH -t 0:30:00
#SBATCH --export=ALL


source /home/fs02/pmr82_0001/ah986/rival_framings/bin/activate
mpiexec -n 1 -usize 20 python3 statemod_data_extraction.py -i ./ids.txt