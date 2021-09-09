import numpy as np
import os
from numpy.lib.recfunctions import structured_to_unstructured
import scipy.spatial as ss
import meshzoo
import meshio
from numba import njit, jit, prange
import time

import Util.AMSOS as am


parser = am.getDefaultArgParser('calc local stat on a spherical shell')

parser.add_argument('-r', '--rad', type=float,
                    default=0.25,
                    help='average radius')
parser.add_argument('-n', '--nseg', type=int,
                    default=20,
                    help='number of segments per each MT')
parser.add_argument('-m', '--mesh', type=int,
                    default=50,
                    help='order of icosa mesh')

args = parser.parse_args()

config = am.parseConfig(args.config)

R0 = config['boundaries'][0]['radius']
R1 = config['boundaries'][1]['radius']

center = np.array(config['boundaries'][0]['center'])
Rc = (R0+R1)*0.5
radAve = args.rad
nseg = args.nseg  # split each MT into nseg segments
mesh_order = args.mesh
# a cylinder with height R1-R0, approximate
volAve = np.pi*radAve*radAve*np.abs(R1-R0)
foldername = 'LocalOrder'

print(center, Rc, radAve, nseg, mesh_order, foldername, volAve)


am.mkdir(foldername)

points, cells = meshzoo.icosa_sphere(mesh_order)

er, etheta, ep = am.e_sph(xyz=points)

for i in range(points.shape[0]):
    p = points[i, :]
    p = p*Rc
    points[i, :] = p+center


def ll2array(listoflist, dtype, padding):
    n = len(max(listoflist, key=len))
    lst_2 = [x + [padding]*(n-len(x)) for x in listoflist]

    return np.array(lst_2, dtype=dtype)


@njit(parallel=True)
def calcT(N: int, volAve: float, search, seg_vec, seg_len, etheta):
    volfrac = np.zeros(N)
    nematic = np.zeros(N)
    polarity_theta = np.zeros(N)
    polarity = np.zeros((N, 3))
    for i in prange(N):
        idx = []
        for id in search[i]:
            if id != -1:
                idx.append(id)
            else:
                break

        if len(idx) != 0:
            vecList = np.zeros((len(idx), 3))
            len_sum = 0
            for k in range(len(idx)):
                id = idx[k]
                vecList[k] = seg_vec[id]
                len_sum += seg_len[id]
            volfrac[i] = am.volMT(0.0125, len_sum)/volAve
            nematic[i] = am.calcNematicS_numba(vecList)
            polarity[i] = am.calcPolarP_numba(vecList)
            polarity_theta[i] = np.dot(polarity[i], etheta[i])

    return (volfrac, nematic, polarity, polarity_theta)


@njit(parallel=True)
def calcP(N: int, volAve: float, search, Pbind):
    xlinker_n_all = np.zeros(N)
    xlinker_n_db = np.zeros(N)
    for i in prange(N):
        idx = []
        for id in search[i]:
            if id != -1:
                idx.append(id)
            else:
                break

        if len(idx) != 0:
            xlinker_n_all[i] = len(idx)/volAve
            xlinker_n_db[i] = 0
            for id in idx:
                if Pbind[id, 0] != -1 and Pbind[id, 1] != -1:
                    xlinker_n_db[i] += 1
            xlinker_n_db[i] /= volAve

    return (xlinker_n_all, xlinker_n_db)


def calcLocalOrder(frame, pts, rad):
    '''pts: sample points, rad: average radius'''
    # step1: build cKDTree with TList center
    # step2: sample the vicinity of every pts
    # step3: compute average vol, P, S for every point

    TList = frame.TList
    Tm = structured_to_unstructured(TList[['mx', 'my', 'mz']])
    Tp = structured_to_unstructured(TList[['px', 'py', 'pz']])
    Tvec = Tp-Tm  # vector
    Tlen = np.linalg.norm(Tvec, axis=1)  # length
    Tdct = Tvec/Tlen[:, np.newaxis]  # unit vector
    NMT = TList.shape[0]
    seg_center = np.zeros((nseg*NMT, 3))
    seg_vec = np.zeros((nseg*NMT, 3))
    seg_len = np.zeros(nseg*NMT)

    Npts = pts.shape[0]

    for i in range(nseg):
        seg_center[i*NMT:(i+1)*NMT, :] = Tm+((i+0.5)*1.0/nseg) * Tvec
        seg_vec[i*NMT:(i+1)*NMT, :] = Tdct
        seg_len[i*NMT:(i+1)*NMT] = Tlen/nseg

    tree = ss.cKDTree(seg_center)
    search = tree.query_ball_point(pts, rad, workers=-1, return_sorted=False)
    search = ll2array(search, int, -1)

    start = time.time()  # start time
    volfrac, nematic, polarity, polarity_theta = calcT(
        Npts, volAve, search, seg_vec, seg_len, etheta)
    end = time.time()
    print("T time is  {}".format(end-start))

    PList = frame.PList
    Pm = structured_to_unstructured(PList[['mx', 'my', 'mz']])
    Pp = structured_to_unstructured(PList[['px', 'py', 'pz']])
    Pbind = structured_to_unstructured(PList[['idbind0', 'idbind1']])

    centers = 0.5*(Pm+Pp)
    tree = ss.cKDTree(centers)
    search = tree.query_ball_point(pts, rad, workers=-1, return_sorted=False)
    search = ll2array(search, int, -1)

    start = time.time()  # start time
    xlinker_n_all, xlinker_n_db = calcP(Npts, volAve, search, Pbind)
    end = time.time()
    print("P time is  {}".format(end-start))

    name = am.get_basename(frame.filename)
    meshio.write_points_cells(foldername+"/sphere_{}.vtu".format(name), points,
                              cells=[("triangle", cells)],
                              point_data={'volfrac': volfrac,
                                          'nematic': nematic,
                                          'polarity': polarity,
                                          'polarity_theta': polarity_theta,
                                          'xlinker_n_all': xlinker_n_all,
                                          'xlinker_n_db': xlinker_n_db
                                          })
    return


SylinderFileList = am.getFileListSorted(
    './result*-*/SylinderAscii_*.dat', info=False)

for file in SylinderFileList[10:11]:
    frame = am.FrameAscii(file, readProtein=True, sort=False, info=True)
    calcLocalOrder(frame, points, radAve)

# Parallel(n_jobs=2, max_nbytes=1e5)(delayed(calcLocalOrder)(
#     am.FrameAscii(f, readProtein=True, sort=True, info=False), points, radAve) for f in SylinderFileList[:12])
