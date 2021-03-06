#!/usr/bin/env python

"""@package docstring
File: runlog_funcs.py
Author: Adam Lamson
Email: alamson@flatironinstitute.org
Description:
"""

import re
import time

import numpy as np

from datetime import datetime


def get_walltime(log_path):
    """Uses the log file to calculate the total time the simulation took.
    This will not work for restarted simulations. Might want to fix that.

    @param log_path TODO
    @return: TODO

    """
    with open(log_path, 'r') as rlf:
        pattern = re.compile(r'\[(\d+-\d+-\d+\s\d+:\d+:\d+\.\d+)\]')
        line = rlf.readline()
        while not pattern.search(line):
            line = rlf.readline()
        start_wtime = pattern.search(line).group(0)

        for line in reversed(rlf.readlines()):
            if not pattern.search(line):
                continue
            end_wtime = pattern.search(line).group(0)
            break

    stripstr = '[%Y-%m-%d %H:%M:%S.%f]'
    end_dt = datetime.strptime(end_wtime, stripstr)
    start_dt = datetime.strptime(start_wtime, stripstr)
    return end_dt - start_dt


def get_wt_timestep(log_path):
    """Get the wall time for every time step.
    (Might want to add an option to coarse grain.)

    @param log_path Path to run.log
    @return: Times between timesteps

    """
    with open(log_path, 'r') as rlf:
        time_ptrn = re.compile(
            r'\[(\d+-\d+-\d+\s\d+:\d+:\d+\.\d+)\].*CurrentStep\W+(\d+)')
        stripstr = '%Y-%m-%d %H:%M:%S.%f'
        wt_arr = []
        for line in rlf:
            re_match = time_ptrn.search(line)
            if re_match:
                if not int(re_match.group(2)):
                    continue
                wt_arr += [
                    datetime.strptime(
                        time_ptrn.search(line).group(1),
                        stripstr)]

    fconv = np.vectorize(lambda x: x.total_seconds())
    wt_arr = np.array(wt_arr)
    return fconv(wt_arr[1:] - wt_arr[:-1])


##########################################
if __name__ == "__main__":
    print("Not implemented yet")
