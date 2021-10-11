#!/bin/bash
#SBATCH --nodes=1                   # Use one node
#SBATCH --ntasks=1                  # Run a single task
#SBATCH --time 2:30:00
#SBATCH --export=ALL
#SBATCH --mail-user=ah986@cornell.edu
#SBATCH --mail-type=ALL
#SBATCH --array=1-10                # Array range

source /home/fs02/pmr82_0001/ah986/envs/rival_framings/bin/activate

START_NUM=0
END_NUM=99

# Run the loop of runs for this task.
for (( run=$START_NUM; run<=END_NUM; run++ )); do
  echo This is SLURM task $SLURM_ARRAY_TASK_ID, run number $run
  srun python3 extract_xdd_flow_only.py ../LHsamples_wider_100_AnnQonly/cm2015B_S${run}_${SLURM_ARRAY_TASK_ID}.xdd
done


