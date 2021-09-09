#!/usr/bin/env python3

# SBATCH --nodes=4
# SBATCH --ntasks-per-node=16
# SBATCH --cpus-per-task=1
# SBATCH -p normal
# SBATCH -t 03:00:00
# SBATCH --exclusive
# SBATCH --job-name xdd_to_parquet

import concurrent.futures.thread
import argparse
import dask.dataframe as dd
from glob import glob
from importlib.util import find_spec, module_from_spec
import io
from joblib import Parallel, delayed
import logging
import numpy as np
import pandas as pd
from pathlib import Path
import re
import shutil
import sys
from timeit import default_timer as timer
from typing import Iterable

mpi_module = 'mpi4py.MPI'
mpi_futures = 'mpi4py.futures'


class StateModDataExtractor:
    """Class to handle extracting structure, sample, and realization data from StateMod xdd files."""

    def __init__(
            self,
            structure_ids_file_path: str,
            temporary_path: str,
            output_path: str,
            glob_to_xdd: str = None,
            allow_overwrite: bool = False,
            has_mpi: bool = False
    ):

        # path to file with the structure ids of interest separated by newlines
        # absolute path is best; relative path must be relative to where you run from
        self.structure_ids_file_path = structure_ids_file_path
        self.ids_of_interest = np.genfromtxt(self.structure_ids_file_path, dtype='str').tolist()

        # output path
        # be sure to look at the log file generated here after running
        # absolute path is best; relative path must be relative to where you run from
        self.output_path = output_path
        self.temporary_path = temporary_path

        # allow overwriting files in the output directory
        # this check is implemented in a simplistic way:
        #   - do any parquet files exist in output_path or not
        self.allow_overwrite = allow_overwrite

        # is mpi in use and loaded
        self.use_mpi = has_mpi

        # expected data format
        self.metadata_rows = np.arange(1, 12)
        self.id_column = 0
        self.id_column_name = 'structure_id'
        self.id_column_type = object
        self.year_column = 2
        self.year_column_name = 'year'
        self.year_column_type = np.uint16
        self.month_column = 3
        self.month_column_name = 'month'
        self.demand_column = 4
        self.month_column_type = object
        self.demand_column_name = 'demand'
        self.demand_column_type = np.uint32
        self.shortage_column = 17
        self.shortage_column_name = 'shortage'
        self.shortage_column_type = np.uint32

        # these columns will be added to all rows
        self.sample_column_name = 'sample'
        self.sample_column_type = np.uint16
        self.realization_column_name = 'realization'
        self.realization_column_type = np.uint8

    def create_file_per_structure_id(self, structure_id: str) -> bool:
        """Reads a collection of parquet files and aggregates values for a structure_id into a single parquet file.

        Args:
            structure_id (str): the structure_id to aggregate

        Returns:
            bool: a boolean indicating whether aggregation was successful (True means success)
        """

        df = dd.read_parquet(
            Path(f'{self.temporary_path}/**/S*_*_*.parquet'),
            engine='pyarrow-dataset', filters=[['structure_id', '=', structure_id]]
        ).compute()
        if len(df.index) == 0:
            logging.warning(f'No data for for structure_id: {structure_id}.')
            return False
        if not self.validate_data(df):
            logging.warning(f'WARNING: Anomalous data detected for structure_id: {structure_id}.')
        df.to_parquet(
            Path(f'{self.output_path}/{structure_id}.parquet'),
            engine='pyarrow',
            compression='gzip'
        )
        return True

    def validate_data(self, dataframe: pd.DataFrame) -> bool:
        """Attempts to determine if the data makes sense

        Args:
            dataframe (pd.DataFrame): the data to validate

        Returns:
            bool: a boolean indicating whether validation was successful (True means valid)
        """
        # TODO figure out how to validate data
        # TODO i.e. anomaly detection
        return True

    @staticmethod
    def pretty_timer(seconds: float) -> str:
        """Formats an elapsed time in a human friendly way.

        Args:
            seconds (float): a duration of time in seconds

        Returns:
            str: human friendly string representing the duration
        """
        if seconds < 1:
            return f'{round(seconds * 1.0e3, 0)} milliseconds'
        elif seconds < 60:
            return f'{round(seconds, 3)} seconds'
        elif seconds < 3600:
            return f'{int(round(seconds) // 60)} minutes and {int(round(seconds) % 60)} seconds'
        elif seconds < 86400:
            return f'{int(round(seconds) // 3600)} hours, {int((round(seconds) % 3600) // 60)} minutes, and {int(round(seconds) % 60)} seconds '
        else:
            return f'{int(round(seconds) // 86400)} days, {int((round(seconds) % 86400) // 3600)} hours, and {int((round(seconds) % 3600) // 60)} minutes'

    def extract(self):
        """Perform the data extraction"""

        # start a timer to track how long this takes
        t = timer()

        if not self.ids_of_interest or len(self.ids_of_interest) == 0:
            raise IOError(f"No structure_ids found in {self.structure_ids_file_path}. Aborting.")

        # check if output directory exists
        if not Path(self.output_path).is_dir():
            # create it if not
            Path(self.output_path).mkdir(parents=True, exist_ok=True)
        else:
            # check if it already has parquet files in it
            if len(list(Path(self.output_path).glob('*.parquet'))) > 0:
                # if overwrite not allowed, abort
                if not self.allow_overwrite:
                    raise FileExistsError(
                        'Parquet files exist in the output directory; ' +
                        'please move them or set `allow_overwrite` to True.'
                    )
        # create a temporary directory in output path to store intermediate files
        if not Path(self.temporary_path).is_dir():
            Path(self.temporary_path).mkdir(parents=True, exist_ok=True)
        elif len(list(Path(self.temporary_path).glob('*'))) > 0:
            # if the temporary path already has files, abort if overwrite not allowed
            raise FileExistsError(
                f'The temporary file path {self.temporary_path} ' +
                'already contains files; please move them or set `allow_overwrite` to True.'
            )

        # setup logging
        logging.basicConfig(
            level='INFO',
            format='%(asctime)s - %(filename)s: %(message)s',
            datefmt='%m/%d/%Y %I:%M:%S %p',
            handlers=[
                logging.FileHandler(Path(f'{self.output_path}/log.log')),
                logging.StreamHandler()
            ]
        )

        # check if MPI is available
        # if so, use mpi4py
        # if not, use joblib
        if self.use_mpi:
            context = futures.MPIPoolExecutor
            logging.info(f"Running with mpi4py; world size =  {mpi.COMM_WORLD.Get_size()}.")
        else:
            context = Parallel
            logging.info("Running with joblib.")

        with context(**(dict() if self.use_mpi else dict(n_jobs=-1, temp_folder=self.temporary_path))) as executor:

            # aggregate the temporary files per structure_id to create the final output files
            logging.info('Aggregating structure_id data to parquet files.')
            if self.use_mpi:
                successful_structure_id = executor.map(
                    self.create_file_per_structure_id,
                    self.ids_of_interest,
                    unordered=True
                )
            else:
                successful_structure_id = executor(
                    delayed(self.create_file_per_structure_id)(structure_id) for structure_id in self.ids_of_interest
                )
            # check how many failed
            failed_parquet = [
                self.ids_of_interest[i] for i, status in enumerate(successful_structure_id) if status is False
            ]
            if len(failed_parquet) > 0:
                logging.error(
                    "Failed to create parquet files for the following structure_ids:\n" + "\n".join(failed_parquet)
                )


if __name__ == '__main__':

    use_mpi = False
    mpi_spec = find_spec(mpi_module)
    if mpi_module in sys.modules:
        use_mpi = True
    elif mpi_spec is not None:
        mpi = module_from_spec(mpi_spec)
        futures_spec = find_spec(mpi_futures)
        futures = module_from_spec(futures_spec)
        sys.modules[mpi_module] = mpi
        sys.modules[mpi_futures] = futures
        mpi_spec.loader.exec_module(mpi)
        futures_spec.loader.exec_module(futures)
        if mpi.COMM_WORLD.Get_size() > 1:
            use_mpi = True

    if not use_mpi or mpi.COMM_WORLD.Get_rank() == 0:

        parser = argparse.ArgumentParser(
            description=
            "Extract data from XDD files for a given set of structure IDs, producing a parquet file for each ID."
        )
        parser.add_argument(
            '-f',
            '--force',
            action='store_true',
            dest='force',
            help="allow overwriting existing parquet files (default: false)"
        )
        parser.add_argument(
            '-i',
            '--ids',
            metavar='/path/to/id/file',
            action='store',
            required=True,
            dest='ids',
            help="path to a file containing whitespace delimited structure ids of interest (required)"
        )
        parser.add_argument(
            '-o',
            '--output',
            metavar='/path/to/output/directory',
            action='store',
            default=Path('./output'),
            dest='output',
            help="path to a directory to write the output files (default: './output')"
        )

        parser.add_argument(
            '-t',
            '--temporary',
            metavar='/path/to/temporary/parquet/directory',
            action='store',
            default=Path('./xdd_parquet'),
            dest='xdd_parquet',
            help="path to a directory to the temporary parquet files (default: './xdd_parquet')"
        )

        args = parser.parse_args()

        extractor = StateModDataExtractor(
            allow_overwrite=args.force,
            output_path=args.output,
            structure_ids_file_path=args.ids,
            has_mpi=use_mpi
        )
        extractor.extract()