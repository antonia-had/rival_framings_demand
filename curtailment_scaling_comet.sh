#!/bin/bash
#SBATCH --partition=compute
#SBATCH --ntasks=1440
#SBATCH --time=48:00:00

module load parallel
module load miniconda
source activate /home/ah986/miniconda3/envs/adaptive_demands
# This specifies the options used to run srun. The "-N1 -n1" options are
# used to allocates a single core to each task.
srun="srun --export=all --exclusive -N1 -n1"
# This specifies the options used to run GNU parallel:
#
#   --delay of 0.2 prevents overloading the controlling node.
#
#   -j is the number of tasks run simultaneously.
#
#   The combination of --joblog and --resume create a task log that
#   can be used to monitor progress.
#
parallel="parallel --delay 0.2 -j $SLURM_NTASKS --joblog curtailment_scaling_$3.log"
echo "Submitting samples $1 to $2"
vals=($(seq $1 $2))
$parallel "$srun python3 curtailment_scaling.py" ::: {1..100} ::: {1..10} ::: "${vals[@]}"
