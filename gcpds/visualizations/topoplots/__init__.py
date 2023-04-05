import mne
import numpy as np
import matplotlib
from matplotlib import pyplot as plt


# ----------------------------------------------------------------------
def topoplot(data, channels, montage_name='standard_1020', cmap='coolwarm', resolution=64, interp='cubic', contours=0, ax=None, vmin=None, vmax=None):
    """"""
    info = mne.create_info(
        channels,
        sfreq=1,
        ch_types="eeg",
    )
    info.set_montage(montage_name)

    if ax is None:
        ax = plt.subplot(111)

    mne.viz.plot_topomap(data,
                         info,
                         axes=ax,
                         names=channels,
                         sensors=False,
                         # show_names=True,
                         contours=contours,
                         cmap=cmap,
                         outlines='head',
                         res=resolution,
                         extrapolate='head',
                         show=False,
                         image_interp=interp,
                         vlim=(vmin, vmax),
                         )

    # plt.close()
    return ax
