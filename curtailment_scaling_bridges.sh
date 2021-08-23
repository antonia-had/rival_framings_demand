#!/bin/bash
#SBATCH -p RM
#SBATCH --ntasks=50
#SBATCH --time=00:30:00
#SBATCH --mail-user=ah986@cornell.edu
#SBATCH --mail-type=ALL

module load anaconda3
eval "$(conda shell.bash hook)"
conda activate /ocean/projects/ees200007p/ah986/.conda/envs/adaptive_demands

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
parallel="parallel --delay 0.2 -j $SLURM_NTASKS --joblog curtailment_scaling_$3.log --resume"
echo "Submitting samples $1 to $2"
vals=($(seq $1 $2))

$srun $parallel "echo "$SLURM_PROCID" python3 python_test.py" ::: {1..100} ::: {1..10} ::: "${vals[@]}"

