#!/usr/bin/env python

"""@package docstring
File: nematic_fluctuation_alg.py
Author: Adam Lamson
Email: alamson@flatironinstitute.org
Description: Script to find nematic fluctuations and structure factos
"""

import yaml
from pathlib import Path
import h5py
import torch
import numpy as np

import alens_analysis as aa

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"torch device: {device}")


def analyze_nematic_info(
    h5_file: Path,
    k_points: int = 100,
    n_time_points: int = 100,
    ts_start: int = 100,
):
    """!@brief Analyze nematic information from raw data and save to file

    @param h5_file: Path to raw data file
    @param out_file: Path to save analyzed data
    """
    # Load in raw data
    with h5py.File(h5_file, "r") as h5_data:
        param_dict = yaml.load(h5_data.attrs["RunConfig"], Loader=yaml.FullLoader)
        protein_dict = yaml.load(h5_data.attrs["ProteinConfig"], Loader=yaml.FullLoader)
        box_lower = np.array(param_dict["simBoxLow"])
        box_upper = np.array(param_dict["simBoxHigh"])
        time_arr = h5_data["time"][
            :
        ]  # Load in time array, [:] loads data as numpy array
        # Load in sylinder data
        sy_dat = h5_data["raw_data/sylinders"][...]

    # Fix periodic boundary conditions
    sy_dat = aa.helpers.apply_pbc_to_raw_syl_data(
        sy_dat, box_lower, box_upper, device=device
    )

    # Calculate nematic order parameter
    nematic_order = aa.nematic_order.calc_nematic_order(sy_dat)

    # Calculate nematic director
    nematic_director = aa.nematic_order.calc_nematic_director(sy_dat, device=device)

    # Calculate structure factor and fluctuations
    time_step = (len(time_arr) - ts_start) // n_time_points

    Sx_time_arr = np.zeros((k_points, n_time_points))
    Sy_time_arr = np.zeros((k_points, n_time_points))
    Sz_time_arr = np.zeros((k_points, n_time_points))

    tk_arr = torch.logspace(-1, 2, k_points)
    tkx_arr = torch.vstack([tk_arr, torch.zeros(k_points), torch.zeros(k_points)]).T.to(
        device
    )
    tky_arr = torch.vstack([torch.zeros(k_points), tk_arr, torch.zeros(k_points)]).T.to(
        device
    )
    tkz_arr = torch.vstack([torch.zeros(k_points), torch.zeros(k_points), tk_arr]).T.to(
        device
    )

    for i in range(n_time_points):
        print(i)
        com_arr = 0.5 * (
            sy_dat[:, 2:5, ts_start + i * time_step]
            + sy_dat[:, 5:8, ts_start + i * time_step]
        )
        tcom_arr = torch.from_numpy(com_arr).to(device)
        dir_arr = (
            sy_dat[:, 5:8, ts_start + i * time_step]
            - sy_dat[:, 2:5, ts_start + i * time_step]
        )

        tQ_arr = torch.from_numpy(aa.nematic_order.make_nematic_tensor_arr(dir_arr)).to(
            device
        )
        tQ_arr -= tQ_arr.mean(axis=0)

        for j in range(k_points):
            Sx_time_arr[j, i] = aa.nematic_order.make_structure_factor_torch(
                tQ_arr, tcom_arr, tkx_arr[j], device=device
            )
            Sy_time_arr[j, i] = aa.nematic_order.make_structure_factor_torch(
                tQ_arr, tcom_arr, tky_arr[j], device=device
            )
            Sz_time_arr[j, i] = aa.nematic_order.make_structure_factor_torch(
                tQ_arr, tcom_arr, tkz_arr[j], device=device
            )

    # Calculate nematic fluctuations

    # Store data
    #  time_arr
    #  nematic_order
    #  nematic_director
    #  nematic_structure_factor
    #  nematic_fluctuation

    return
