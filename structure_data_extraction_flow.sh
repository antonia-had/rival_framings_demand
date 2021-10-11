#!/bin/bash
#SBATCH --nodes=1                   # Use one node
#SBATCH --ntasks=1                  # Run a single task
#SBATCH --time 2:30:00
#SBATCH --export=ALL
#SBATCH --mail-user=ah986@cornell.edu
#SBATCH --mail-type=ALL
#SBATCH --array=1-7                # Array range

source /home/fs02/pmr82_0001/ah986/rival_framings/bin/activate

#Set the number of runs that each SLURM task should do
PER_TASK=49

# Calculate the starting and ending values for this task based
# on the SLURM task and the number of runs per task.
START_NUM=$(( ($SLURM_ARRAY_TASK_ID - 1) * $PER_TASK + 1 ))
END_NUM=$(( $SLURM_ARRAY_TASK_ID * $PER_TASK ))


# Run the loop of runs for this task.
for (( run=$START_NUM; run<=END_NUM; run++ )); do
  ID=$(sed -n "$run"p ids.txt)
  echo This is SLURM task $SLURM_ARRAY_TASK_ID, run number $run, structure $ID
  srun python3 structure_data_extraction_flow.py ./structure_outputs ./xdd_parquet_flow/ $ID
done


