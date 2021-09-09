#!/bin/bash

for i in $(seq 1 100); do
  for k in $(seq 1 600); do
    for j in $(seq 1 10); do
      file="xdd_parquet/S${i}_${j}/S${i}_${j}_${k}.parquet"
      if [ ! -f $file ]; then
        echo -e "python3 curtailment_scaling.py $i $k" >> missing_runs.txt
        break
      fi
    done
  done
done
