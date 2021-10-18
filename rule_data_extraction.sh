#!/bin/bash
#SBATCH --nodes=1                   # Use one node
#SBATCH --ntasks-per-node=1                 # Run a single task
#SBATCH --exclusive=user
#SBATCH --time 10:00:00
#SBATCH --mail-user=ah986@cornell.edu
#SBATCH --mail-type=ALL
#SBATCH --array=1-15                # Array range

source /home/fs02/pmr82_0001/ah986/rival_framings/bin/activate

#Set the number of tasks that each SLURM task should do
PER_TASK=40

# Calculate the starting and ending values for this task based
# on the SLURM task and the number of runs per task.
START_NUM=$(( ($SLURM_ARRAY_TASK_ID - 1) * $PER_TASK + 1 ))
END_NUM=$(( $SLURM_ARRAY_TASK_ID * $PER_TASK ))


# Run the loop of runs for this task.
for (( rule=$START_NUM; rule<=END_NUM; rule++ )); do
  echo This is SLURM task $SLURM_ARRAY_TASK_ID, run extraction for $rule
  srun python3 rule_data_extraction.py $rule
done
