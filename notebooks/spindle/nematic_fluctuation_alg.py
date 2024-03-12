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

import alens_analysis as aa

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f'torch device: {device}')

# Load in raw data
with h5py.File(next(opts.analysis_dir.glob('raw*.h5')), 'r') as h5_data:
    param_dict = yaml.load(h5_data.attrs['RunConfig'], Loader=yaml.FullLoader)  
    protein_dict = yaml.load(h5_data.attrs['ProteinConfig'], Loader=yaml.FullLoader)  
    box_lower = np.array(param_dict['simBoxLow'])
    box_upper = np.array(param_dict['simBoxHigh'])
    time_arr = h5_data['time'][:] # Load in time array, [:] loads data as numpy array
    # Load in sylinder data
    sy_dat = h5_data['raw_data/sylinders'][...]

# Fix periodic boundary conditions

# Calculate nematic order parameter

# Calculate nematic director

# Calculate structure factor 

# Calculate nematic fluctuations

# Store data