# Steps to replicate this experiment

## 1. Generate sample and lists of which demands get reduced

`generate_sample_info.py`

## 2. Calculate monthly and annual flows per realization
These flows are used to trigger adaptive demands. Creates one for every state of the world and every realization. 
`realization_flows.py`
Can be run in parallel using `realization_flows.sh` (< this script has been edited and needs to be checked).

## 3. Calculate adaptive demands, write new inputs, execute realization, and parse to .parquet files 
This is handled by `curtailment_scaling.py` which can be run in parallel (in batches) using `curtailment_scaling_expanse.sh`.
This produces a compressed `.parquet` file, by converting the `.xdd` output file of each run. 

## 4. Create combined files
Scripts in `data_extraction.py` can be used to:
 * create combined files for each user for each realization with all 600 rules together
 * create combined files for each user for all realizations and all rules (these files end up being very large and inconvenient to work with)


