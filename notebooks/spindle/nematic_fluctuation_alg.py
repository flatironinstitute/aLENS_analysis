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

from alens_analysis.helpers import Timer

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
        time_arr = h5_data["time"][:]
        sy_dat = h5_data["raw_data/sylinders"][...]

    if len(time_arr) < ts_start:
        print("Not enough time points to start analysis.")
        return

    # Fix periodic boundary conditions
    sy_dat = aa.helpers.apply_pbc_to_raw_syl_data(
        sy_dat, box_lower, box_upper, device=device
    )

    # Store time array and run parameters
    with h5py.File(h5_file.parent / "nematic_analysis.h5", "w") as h5_nem_data:
        h5_nem_data.create_dataset("time", data=time_arr)
        h5_nem_data.attrs["RunConfig"] = yaml.dump(param_dict)
        h5_nem_data.attrs["ProteinConfig"] = yaml.dump(protein_dict)

    timer = Timer()
    # Calculate nematic order parameter
    nematic_order = aa.nematic_order.calc_nematic_order(sy_dat)
    with h5py.File(h5_file.parent / "nematic_analysis.h5", "a") as h5_nem_data:
        h5_nem_data.create_dataset("nematic_order", data=nematic_order)
    print("Made nematic order array")
    timer.log()

    # Calculate nematic director
    timer.milestone()
    nematic_director = aa.nematic_order.calc_nematic_director_arr(sy_dat, device=device)
    with h5py.File(h5_file.parent / "nematic_analysis.h5", "a") as h5_nem_data:
        h5_nem_data.create_dataset("nematic_director", data=nematic_director)
    print("Made nematic director array")
    timer.log()

    # Calculate Q-tensor structure factor and fluctuations
    tk_arr = torch.logspace(-1, 2, k_points)
    with h5py.File(h5_file.parent / "nematic_analysis.h5", "a") as h5_nem_data:
        h5_nem_data.create_dataset("k", data=tk_arr.to("cpu"))

    tkx_arr = torch.vstack([tk_arr, torch.zeros(k_points), torch.zeros(k_points)]).T.to(
        device
    )
    tky_arr = torch.vstack([torch.zeros(k_points), tk_arr, torch.zeros(k_points)]).T.to(
        device
    )
    tkz_arr = torch.vstack([torch.zeros(k_points), torch.zeros(k_points), tk_arr]).T.to(
        device
    )

    com_arr = 0.5 * (sy_dat[:, 2:5, :] + sy_dat[:, 5:8, :])
    tcom_arr = torch.from_numpy(com_arr).to(device)
    dir_arr = sy_dat[:, 5:8, :] - sy_dat[:, 2:5, :]
    tdir_arr = torch.from_numpy(dir_arr).to(device)

    time_step = (len(time_arr) - ts_start) // n_time_points

    # Full Q-tensor structure factor
    timer.milestone()
    Sx_time_arr = torch.zeros((k_points, n_time_points)).to(device)
    Sy_time_arr = torch.zeros((k_points, n_time_points)).to(device)
    Sz_time_arr = torch.zeros((k_points, n_time_points)).to(device)
    for i in range(n_time_points):
        time_ind = ts_start + i * time_step
        tdir = tdir_arr[:, :, time_ind]
        tcom = tcom_arr[:, :, time_ind]

        tQ_arr = aa.nematic_order.make_nematic_tensor_arr(tdir, device)

        Sx_time_arr[:, i] = aa.nematic_order.make_structure_factor_torch_fast(
            tQ_arr, tcom, tkx_arr, device=device
        )
        Sy_time_arr[:, i] = aa.nematic_order.make_structure_factor_torch_fast(
            tQ_arr, tcom, tky_arr, device=device
        )
        Sz_time_arr[:, i] = aa.nematic_order.make_structure_factor_torch_fast(
            tQ_arr, tcom, tkz_arr, device=device
        )

    with h5py.File(h5_file.parent / "nematic_analysis.h5", "a") as h5_nem_data:
        h5_nem_data.create_dataset("nematic_structure_x", data=Sx_time_arr.to("cpu"))
        h5_nem_data.create_dataset("nematic_structure_y", data=Sy_time_arr.to("cpu"))
        h5_nem_data.create_dataset("nematic_structure_z", data=Sz_time_arr.to("cpu"))
    print("Made nematic structure factor array")
    timer.log()

    # Calculate nematic fluctuations
    timer.milestone()
    dSx_time_arr = torch.zeros((k_points, n_time_points))
    dSy_time_arr = torch.zeros((k_points, n_time_points))
    dSz_time_arr = torch.zeros((k_points, n_time_points))

    for i in range(n_time_points):
        time_ind = ts_start + i * time_step
        tdir = tdir_arr[:, :, time_ind]
        tcom = tcom_arr[:, :, time_ind]

        tQ_arr = aa.nematic_order.make_nematic_tensor_arr(tdir, device)
        # We want to fluctuations
        tQ_arr -= tQ_arr.mean(axis=0)

        dSx_time_arr[:, i] = aa.nematic_order.make_structure_factor_torch_fast(
            tQ_arr, tcom, tkx_arr, device=device
        )
        dSy_time_arr[:, i] = aa.nematic_order.make_structure_factor_torch_fast(
            tQ_arr, tcom, tky_arr, device=device
        )
        dSz_time_arr[:, i] = aa.nematic_order.make_structure_factor_torch_fast(
            tQ_arr, tcom, tkz_arr, device=device
        )

    with h5py.File(h5_file.parent / "nematic_analysis.h5", "a") as h5_nem_data:
        h5_nem_data.create_dataset("nematic_fluctuation_x", data=dSx_time_arr.to("cpu"))
        h5_nem_data.create_dataset("nematic_fluctuation_y", data=dSy_time_arr.to("cpu"))
        h5_nem_data.create_dataset("nematic_fluctuation_z", data=dSz_time_arr.to("cpu"))
    print("Made nematic fluctuation structure factor array")
    timer.log()

    timer.log_total()

    return


if __name__ == "__main__":
    main_test_dir = Path("/mnt/home/alamson/ceph/DATA/Motor_Inference/IsoNemTesting")

    data_files = list(main_test_dir.glob("**/analysis/raw_data.h5"))
    for h5_file in data_files:
        analyze_nematic_info(
            h5_file,
            k_points=100,
            n_time_points=100,
            ts_start=100,
        )
