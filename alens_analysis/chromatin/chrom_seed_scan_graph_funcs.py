#!/usr/bin/env python

"""@package docstring
File: chrom_seed_scan_graph_funcs.py
Author: Adam Lamson
Email: alamson@flatironinstitute.org
Description:
"""
# Basic useful imports
import re
import time
import yaml
from pprint import pprint
from pathlib import Path
import h5py

# Data manipulation
import numpy as np
from scipy.special import erf
from scipy.integrate import quad
import scipy.stats as stats
from scipy.signal import savgol_filter

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.colors as colors

from .chrom_seed_scan_analysis import (get_scan_cond_data,
                                       get_scan_avg_contact_mat,
                                       get_scan_avg_kymo)

from .chrom_graph_funcs import (make_hic_plot, plot_contact_kymo,
                                plot_condensate_avg_contact_vs_time,
                                plot_condensate_size_vs_time)

from .chrom_condensate_analysis import (gen_condensate_track_info,
                                        extract_condensates)


def sd_num(h5_data):
    ydict = yaml.safe_load(h5_data.attrs['RunConfig'])
    return ydict['rngSeed']


def make_all_seed_scan_condensate_graphs(
        h5_scan_data, sd_h5_data_lst, opts, overwrite=False):
    cond_sty = {
        "axes.titlesize": 20,
        "axes.labelsize": 24,
        "lines.linewidth": 2,
        "lines.markersize": 2,
        "xtick.labelsize": 24,
        "ytick.labelsize": 24,
        "font.size": 20,
        "font.sans-serif": 'Helvetica',
        "text.usetex": False,
        'mathtext.fontset': 'cm',
    }
    plt.style.use(cond_sty)
    # Make sure hdf5 data sets are sorted by seed number
    sd_h5_data_lst.sort(key=sd_num)

    # if overwrite and 'analysis' in h5_data.keys():
    #     print('Deleting analysis')
    #     del h5_data['analysis']
    # analysis_grp = h5_data.require_group('analysis')

    # TODO: Cludge - make this better
    ss_ind = sd_h5_data_lst[0]['analysis/pos_kymo'].attrs['timestep_range'][0]
    end_ind = sd_h5_data_lst[0]['analysis/pos_kymo'].attrs['timestep_range'][1]
    time_arr = sd_h5_data_lst[0]['time'][ss_ind:end_ind]
    # TODO: Cludge - make this better
    start_bead = 0
    end_bead = None
    nbeads = sd_h5_data_lst[0]['raw_data']['sylinders'][start_bead:end_bead, 0, 0].shape[0]

    fig1, axarr1 = plt.subplots(1, 3, figsize=(24, 6))
    cond_num_arr, max_width_arr, total_bead_arr = get_scan_cond_data(
        sd_h5_data_lst)
    plot_condensate_num_sd_scan(axarr1[0], time_arr, cond_num_arr)
    plot_condensate_size_sd_scan(
        axarr1[1:], time_arr, max_width_arr, total_bead_arr)
    fig1.tight_layout()
    fig1.savefig(opts.analysis_dir / f'cond_num_size.png')

    fig2, axarr2 = plt.subplots(1, 3, figsize=(24, 6))

    plot_avg_contact_tracks(axarr2[0], sd_h5_data_lst, time_arr)
    plot_cond_size_tracks(axarr2[1], sd_h5_data_lst, time_arr)
    axarr2[0].set_ylim(0)
    axarr2[1].set_ylim(0)

    fig2.tight_layout()
    fig2.savefig(opts.analysis_dir / f'cond_tracks_avgs.png')

    plt.rcParams['image.cmap'] = 'YlOrRd'
    log_avg_contact_mat = get_scan_avg_contact_mat(sd_h5_data_lst)
    fig3, ax3 = make_hic_plot(nbeads, log_avg_contact_mat, vmin=-7.)
    fig3.tight_layout()
    fig3.savefig(opts.analysis_dir / f'log_avg_contact_mat.png')

    fig4, ax4 = plt.subplots(figsize=(8, 6))
    avg_contact_kymo = get_scan_avg_kymo(sd_h5_data_lst)
    plot_contact_kymo(fig4, ax4, time_arr, avg_contact_kymo, vmax=7.)
    fig4.tight_layout()
    fig4.savefig(opts.analysis_dir / f'avg_contact_kymo.png')


def plot_condensate_num_sd_scan(ax, time_arr, cond_num_arr):
    avg_cond_num = cond_num_arr.mean(axis=-1)
    for i in range(cond_num_arr.shape[-1]):
        _ = ax.plot(time_arr, cond_num_arr[:, i], color='k', alpha=.1)

    _ = ax.plot(time_arr, avg_cond_num, color='orange')
    ax.set_xlabel('Time (sec)')
    ax.set_ylabel('Number of condensates')
    ax.set_ylim(0)


def plot_condensate_size_sd_scan(
        axarr, time_arr, max_width_arr, total_bead_arr):
    axarr[0].sharey(axarr[1])
    avg_max_width = max_width_arr.mean(axis=-1)
    avg_total_bead = total_bead_arr.mean(axis=-1)
    for i in range(max_width_arr.shape[-1]):
        _ = axarr[0].plot(time_arr, max_width_arr[:, i], color='k', alpha=.1)
        _ = axarr[1].plot(time_arr, total_bead_arr[:, i], color='k', alpha=.1)

    _ = axarr[0].plot(time_arr, avg_max_width, color='orange')
    _ = axarr[1].plot(time_arr, avg_total_bead, color='orange')

    _ = axarr[0].set_title('Beads in largest condensate')
    _ = axarr[1].set_title('Total beads in condensate')

    axarr[0].set_ylim(0)
    axarr[0].set_ylabel('Number of beads')

    axarr[0].set_xlabel('Time (sec)')
    axarr[1].set_xlabel('Time (sec)')


def plot_avg_contact_tracks(ax, sd_h5_data_lst, time_arr):
    for h5_data in sd_h5_data_lst:
        analysis_grp = h5_data['analysis']

        contact_kymo = analysis_grp['contact_kymo'][...]
        nbeads = contact_kymo.shape[0]
        contact_cond_edges = analysis_grp['contact_cond_edges'][...]
        contact_cond_num = analysis_grp['contact_cond_num'][...]
        if 'condensates' not in analysis_grp:
            cond_lst = gen_condensate_track_info(time_arr, contact_cond_edges,
                                                 contact_cond_num)
        else:
            cond_lst = extract_condensates(analysis_grp['condensates'])

        plot_condensate_avg_contact_vs_time(ax, time_arr, contact_kymo, cond_lst,
                                            same_start_flag=True, color='k', alpha=.1)


def plot_cond_size_tracks(ax, sd_h5_data_lst, time_arr):
    for h5_data in sd_h5_data_lst:
        analysis_grp = h5_data['analysis']

        contact_kymo = analysis_grp['contact_kymo'][...]
        nbeads = contact_kymo.shape[0]
        contact_cond_edges = analysis_grp['contact_cond_edges'][...]
        contact_cond_num = analysis_grp['contact_cond_num'][...]
        if 'condensates' not in analysis_grp:
            cond_lst = gen_condensate_track_info(time_arr, contact_cond_edges,
                                                 contact_cond_num)
        else:
            cond_lst = extract_condensates(analysis_grp['condensates'])

        plot_condensate_size_vs_time(ax, time_arr, cond_lst,
                                     same_start_flag=True, color='k', alpha=.1)


    ##########################################
if __name__ == "__main__":
    print("Not implemented yet")
