from gcpds.visualizations.connectivities import CircosConnectivity
import numpy as np
from matplotlib import pyplot as plt

areas = {
    'R-Frontal': ['Fp2'],
    'R-Parietal': ['C4', 'T4', 'A2'],
    'R-Central': ['O2'],

    'L-Central': ['O1'],
    'L-Parietal': ['C3', 'T3', 'A1'],
    'L-Frontal': ['Fp1'],
}


N = 10
v = np.random.normal(size=(N, N))
v = v + v.T  # - np.diag(v.diagonal())
v = (np.abs(v) / v.max()) * 0.8
np.fill_diagonal(v, 1)


arcs = [
    'hemispheres',
    'areas',
    'channels',
]

conn = CircosConnectivity(areas=areas, labelsize=10, arcs=arcs)
conn.connectivity(v, min_alpha=0.5)


conn.bitmap_topoplot()


plt.show()


