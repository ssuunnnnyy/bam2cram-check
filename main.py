"""
Copyright (C) 2016  Genome Research Ltd.

Author: Irina Colgiu <ic4@sanger.ac.uk>

This program is part of bam2cram-check

bam2cram-check is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.
You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

This file has been created on Feb 10, 2016.
"""
import os
import sys
import argparse
import logging
from checks.stats_checks import RunSamtoolsCommands, CompareStatsForFiles
from checks import utils


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', help="File path to the BAM file", required=True)
    parser.add_argument('-input_refgenome', help="File path to the reference genome for the input BAM/CRAM file", required=True)
    parser.add_argument('-c', help="File path to the CRAM file", required=True)
    parser.add_argument('-output_refgenome', help="File path to the reference genome for the compressed BAM/CRAM file", required=True)
    parser.add_argument('-e', help="File path to the error file", required=False)
    parser.add_argument('--log', help="File path to the log file", required=False)
    parser.add_argument('-v', action='count')
    return parser.parse_args()


# To make the default logging to be stdout
def main():
    args = parse_args()
    log_level = (logging.CRITICAL - 10 * args.v) if args.v else logging.INFO
    log_file = args.log if args.log else 'compare_b2c.log'
    logging.basicConfig(level=log_level, format='%(levelname)s - %(asctime)s %(message)s', filename=log_file)
    if args.b and args.c:
        bam_path = args.b
        bam_refgenome = args.input_refgenome
        cram_path = args.c
        cram_refgenome = args.output_refgenome

        if not utils.is_irods_path(bam_path) and not os.path.isfile(bam_path):
            logging.error("This is not a file path: %s" % bam_path)
            #sys.exit(1)
            raise ValueError("This is not a file path: %s")
        if bam_path.endswith('.cram') and not (utils.is_irods_path(bam_refgenome) or os.path.isfile(bam_refgenome)):
            logging.error("The reference genome for the first file has some problem: %s" % bam_refgenome)
            #sys.exit(1)
            raise ValueError("This is not a file path: %s")
        if not utils.is_irods_path(cram_path) and not os.path.isfile(cram_path):
            logging.error("This is not a file path: %s" % cram_path)
            #sys.exit(1)
            raise ValueError("This is not a file path: %s")

        if not utils.is_irods_path(cram_refgenome) and not os.path.isfile(cram_refgenome):
            logging.error("This is not a file path: %s" % cram_refgenome)
            #sys.exit(1)
            raise ValueError("This is not a file path: %s")

        errors = CompareStatsForFiles.compare_bam_and_cram_by_statistics(bam_path, bam_refgenome, cram_path, cram_refgenome)
        if errors:
            if args.e:
                err_f = open(args.e, 'w')
                for err in errors:
                    err_f.write(err + '\n')
                err_f.close()
            else:
                print(errors)
            sys.exit(1)
        else:
            logging.info("There were no errors and no differences between the stats for the 2 files.")


if __name__ == '__main__':
    main()
