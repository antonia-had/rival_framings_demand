#!/bin/bash

for i in $(seq 1 100); do
  for k in $(seq 0 599); do
    for j in $(seq 1 10); do
      file="xdd_parquet/S${i}_${j}/S${i}_${j}_${k}.parquet"
      if [ ! -f $file ]; then
        echo "missing file $i $j $k"
        echo -e "python3 curtailment_scaling.py $i $k" >> missing_runs.txt
        break
      else
        filesize=$(wc -c $file | awk '{print $1}')
        if [ ! $filesize -ge 1000000 ]; then
          echo "smaller size by $i $j $k"
          echo -e "python3 curtailment_scaling.py $i $k" >> missing_runs.txt
          break
        fi
      fi
    done
  done
done
