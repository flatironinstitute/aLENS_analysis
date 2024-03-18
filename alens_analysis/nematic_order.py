#!/usr/bin/env python

"""@package docstring
File: nematic_order.py
Author: Adam Lamson
Email: alamson@flatironinstitute.org
Description:
"""

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import torch


def calc_nematic_order(syls):
    """Calculate the nematic order parameter for a set of syls

    :syls: Raw sylinder data from HDF5 file. PBCs should be applied.
    :returns: Array of nematic order parameters for each frame

    """

    # Get necessary derived functions
    directions = syls[:, 5:8, :] - syls[:, 2:5, :]
    lengths = np.linalg.norm(directions, axis=1)
    unit_dirs = directions / lengths[:, None, :]
    n_syls = syls.shape[0]

    # nematic_tensor averaged over all sylinders
    nematic_tensor = np.einsum("ijk,ilk->jlk", unit_dirs, unit_dirs) / n_syls - (
        np.eye(3)[:, :, np.newaxis] / 3.0
    )

    # Fastest way to calculate nematic order parameter
    # You can prove that this is true by using the fact that the nematic order parameter is the largest eigenvalue of the nematic tensor and the tensor is Q_ab = S(<n_a n_b> - 1/3 delta_ab) where n_a is the director and S the order parameter
    nematic_order = np.sqrt(
        1.5 * np.einsum("ijk,ijk->k", nematic_tensor, nematic_tensor)
    )

    return np.array(nematic_order)


def make_nematic_tensor_arr(direct_arr, device="cpu"):
    """Make the nematic tensor from a list of directors
    N x 3 array of directors

    :directors: List of directors
    :returns: Nematic tensor

    """
    lengths = torch.norm(direct_arr, dim=1)
    unit_dirs = direct_arr / lengths[:, None]
    nematic_tensor_arr = (
        torch.einsum("ij,il->ijl", unit_dirs, unit_dirs)
        - torch.eye(3)[:, :].to(device) / 3.0
    )
    return nematic_tensor_arr


def nematic_analysis(direct_arr):
    """Takes in a list of orientations and calculates the average nematic order parameter and director

    Parameters
    ----------
    directors : _type_
        _description_
    """
    n = direct_arr.shape[0]
    lengths = np.linalg.norm(direct_arr, axis=1)
    unit_dirs = direct_arr / lengths[:, None, :]
    nematic_tensor = (
        np.einsum("ij,il->jl", unit_dirs, unit_dirs) - np.eye(3)[:, :, None] / 3.0
    ) / n

    eigvals, eigvecs = np.linalg.eig(nematic_tensor)
    sort_inds = np.argsort(eigvals)
    nem_order = eigvals[sort_inds[-1]]
    nem_director = eigvecs[:, sort_inds[-1]]
    return nem_order, nem_director


def calc_nematic_director_arr(syls, device="cpu"):
    """Calculate the nematic director from a list of directors

    :direct_arr: N x 3 array of directors
    :returns: Nematic director

    """
    # Get necessary derived functions
    directions = syls[:, 5:8, :] - syls[:, 2:5, :]
    lengths = np.linalg.norm(directions, axis=1)
    unit_dirs = directions / lengths[:, None, :]
    n_syls = syls.shape[0]
    nsteps = directions.shape[2]

    # nematic_tensor averaged over all sylinders
    nematic_tensor_arr = np.einsum("ijk,ilk->jlk", unit_dirs, unit_dirs) / n_syls - (
        np.eye(3)[:, :, np.newaxis] / 3.0
    )

    nematic_director_arr = np.zeros((3, nsteps))
    for i in range(nematic_tensor_arr.shape[2]):
        eigvals, eigvecs = np.linalg.eig(nematic_tensor_arr[:, :, i])
        sort_inds = np.argsort(eigvals)
        nematic_director_arr[:, i] = eigvecs[:, sort_inds[-1]]

    nematic_director_arr = np.where(
        nematic_director_arr[2] < 0, -nematic_director_arr, nematic_director_arr
    )
    return nematic_director_arr


def fourier_transform_nematic_tensor_arr(nematic_tensor_arr, r_arr, k=[0.0, 0.0, 1.0]):
    """Take the fourier transform of the nematic tensor array

    :nematic_tensor_arr: N x 3 x N array of nematic tensors
    :returns: Fourier transform of the nematic tensor array

    """
    kr = np.einsum("ni,i->n", r_arr, k)
    fQ = nematic_tensor_arr * (np.cos(kr) + 1j * np.sin(kr))[:, None, None]

    return fQ


def make_structure_factor(Q_arr, r_arr, k):
    """Make the structure factor from the fourier transform of the nematic tensor array

    :fQ: Fourier transform of the nematic tensor array
    :returns: Structure factor

    """

    fQ_arr = fourier_transform_nematic_tensor_arr(Q_arr, r_arr, k=k)

    # Find structure factor
    Snm = np.einsum("nij,mij->nm", fQ_arr, fQ_arr.conj())
    Snm -= np.diag((2.0 / 3.0) * np.ones(Snm.shape[0]))
    return np.mean(Snm).real


def make_structure_factor_torch(tQ_arr, tr_arr, tk_arr, device="cpu"):
    """Make the structure factor from the fourier transform of the nematic tensor array

    :fQ: Fourier transform of the nematic tensor array
    :returns: Structure factor

    """
    # tQ_arr = torch.from_numpy(Q_arr).to(device)
    # tk_arr = torch.from_numpy(k).to(device)
    # tr_arr = torch.from_numpy(r_arr).to(device).double()

    kr = torch.einsum("ni,i->n", tr_arr, tk_arr)
    tfQ_arr = tQ_arr * ((torch.cos(kr) + 1j * torch.sin(kr))[:, None, None])

    # Find structure factor
    Snm = torch.einsum("nij,mij->nm", tfQ_arr, tfQ_arr.conj())
    # Account for n=m case
    Snm -= (2.0 / 3.0) * torch.eye(Snm.shape[0]).to(device)
    return torch.mean(Snm).real


def make_nematic_structure_factor(tQ_arr, tr_arr, tk_arr, chunk_size=10, device="cpu"):
    """Make the structure factor from the fourier transform of the nematic tensor array

    :fQ: Fourier transform of the nematic tensor array
    :returns: Structure factor

    """

    kr = torch.einsum("ni,qi->nq", tr_arr, tk_arr)

    tfQ_arr = torch.einsum("nij,nq->ijq", tQ_arr, (torch.cos(kr) - 1j * torch.sin(kr)))
    del kr
    torch.cuda.empty_cache()

    # Find structure factor
    S_arr = torch.zeros(tfQ_arr.shape[2]).to(device)
    ## Prevent memory overflow with chunking
    n_chunks = tfQ_arr.shape[2] // chunk_size
    chuncks = torch.chunk(tfQ_arr, n_chunks, dim=2)
    cur_ind = 0
    for i, chunck in enumerate(chuncks):
        S = torch.einsum("ijq,ijq->q", chunck, chunck.conj())
        # Account for n=m case
        S -= tr_arr.shape[0] * (2.0)
        S_arr[cur_ind : cur_ind + S.shape[-1]] = S / (tQ_arr.shape[0] ** 2)

        cur_ind += S.shape[-1]
    return S_arr


def make_structure_factor_torch_fast(tr_arr, tk_arr, chunk_size=10, device="cpu"):
    """Make the structure factor from the fourier transform of the nematic tensor array

    :fQ: Fourier transform of the nematic tensor array
    :returns: Structure factor

    """

    kr = torch.einsum("ni,qi->nq", tr_arr, tk_arr)

    # tfr_arr = torch.einsum("nq->q", torch.cos(kr) - 1j * torch.sin(kr))
    tfr_arr = torch.einsum("nq->q", torch.exp(-1j * kr))
    del kr
    torch.cuda.empty_cache()

    # Find structure factor
    n_chunks = tfr_arr.shape[0] // chunk_size
    chuncks = torch.chunk(tfr_arr, n_chunks, dim=0)
    S_arr = torch.zeros(tfr_arr.shape[0]).to(device)
    cur_ind = 0
    for i, chunck in enumerate(chuncks):
        S = torch.einsum("q,q->q", chunck, chunck.conj())
        # Account for n=m case
        S -= tr_arr.shape[0] * (2.0)
        S_arr[cur_ind : cur_ind + S.shape[-1]] = S / (tr_arr.shape[0] ** 2)

        cur_ind += S.shape[-1]
    return S_arr
