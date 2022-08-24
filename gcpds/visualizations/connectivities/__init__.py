import numpy as np
import matplotlib
import pycircos
import mne
from matplotlib import pyplot as plt


########################################################################
class CircosConnectivity:
    """"""
    Garc = pycircos.Garc
    Gcircle = pycircos.Gcircle

    # ----------------------------------------------------------------------
    def __init__(self, connectivities, channels, areas, small_separation=5, big_separation=20,
                 labelsize=10, arcs=['hemispheres', 'areas', 'channels'], min_alpha=0.5, threshold=0,
                 areas_cmap='viridis', arcs_cmap='viridis', size=10,
                 width=50, text=60, separation=40, labelposition=60, arcs_separation=30,
                 hemisphere_color='C6', channel_color='#c5c5c5', connection_width=1,
                 offset=0, remove_CZ=False, markersize=30,
                 fig=None):
        """Constructor"""

        self.areas = areas
        self.arc_c = 0
        self.labelsize = labelsize
        self.areas_cmap = areas_cmap
        self.arcs_cmap = arcs_cmap
        self.width = width
        self.text = text
        self.separation = separation
        self.labelposition = labelposition
        self.arcs_separation = arcs_separation
        self.hemisphere_color = hemisphere_color
        self.channel_color = channel_color
        self.connection_width = connection_width
        self.offset = offset
        self.remove_CZ = remove_CZ
        self.channels = channels
        self.markersize = markersize

        electrodes = sum([len(self.areas[k]) for k in self.areas])

        self.circle_ = self.Gcircle(fig, figsize=(size, size))

        self.small_separation = small_separation
        self.big_separation = big_separation

        self.smin = (360 - ((len(self.areas) - 2) * self.small_separation + (2 * self.big_separation))) / electrodes

        for i, arc in enumerate(arcs, start=1):
            getattr(self, f'arc_{arc}')(level=i)
        self.draw_arcs()

        self.connectivity(connectivities, threshold, min_alpha)

    # ----------------------------------------------------------------------
    def get_level(self, level):
        """"""
        p = 1000 - ((self.width[level] + self.text[level] + self.separation[level]) * level)
        return [p - self.width[level], p]

    # ----------------------------------------------------------------------
    def arc_areas(self, level=2):
        """"""
        i = 0
        for area in self.areas:
            i += 1

            if i % (len(self.areas) / 2):
                sep = self.small_separation
            else:
                sep = self.big_separation

            s = self.smin * len(self.areas[area])

            arc = self.Garc(arc_id=area.replace('_', ' '),
                            facecolor=matplotlib.cm.get_cmap(self.areas_cmap, len(self.areas))(i - 1),
                            edgecolor=matplotlib.cm.get_cmap(self.areas_cmap, len(self.areas))(i - 1),
                            size=s, interspace=sep,
                            raxis_range=self.get_level(level), labelposition=self.labelposition[level],
                            label_visible=True, labelsize=self.labelsize)
            self.circle_.add_garc(arc)

        self.arc_c += 1

    # ----------------------------------------------------------------------
    def arc_channels(self, level=3):
        """"""
        i = 0
        # self.channels = []

        for area in self.areas:
            i += 1

            if i % (len(self.areas) / 2):
                sepe = 0
            else:
                sepe = self.big_separation

            for j, e in enumerate(self.areas[area], start=1):

                if j != len(self.areas[area]):
                    sep = 0
                else:
                    sep = self.small_separation
                    if sepe:
                        sep = sepe

                arc = self.Garc(arc_id=f'{e}', facecolor=self.channel_color, size=self.smin, interspace=sep, raxis_range=self.get_level(level), labelposition=self.labelposition[level], label_visible=True, labelsize=self.labelsize)
                self.circle_.add_garc(arc)

                # self.channels.append(f'{e}')

        self.arc_c += 1

    # ----------------------------------------------------------------------
    def arc_hemispheres(self, level=1):
        """"""
        arc = self.Garc(arc_id='Right hemisphere', facecolor=self.hemisphere_color,
                        edgecolor=self.hemisphere_color, size=180 - self.big_separation,
                        interspace=self.big_separation, raxis_range=self.get_level(level),
                        labelposition=self.labelposition[level], label_visible=True, labelsize=self.labelsize,
                        )
        self.circle_.add_garc(arc)
        arc = self.Garc(arc_id='Left hemisphere', facecolor=self.hemisphere_color,
                        edgecolor=self.hemisphere_color, size=180 - self.big_separation,
                        interspace=self.big_separation, raxis_range=self.get_level(level),
                        labelposition=self.labelposition[level], label_visible=True, labelsize=self.labelsize,
                        )
        self.circle_.add_garc(arc)
        self.arc_c += 1

    # ----------------------------------------------------------------------
    def draw_arcs(self):
        """"""
        self.circle_.set_garcs((self.big_separation / 2) + (self.offset * (self.smin + self.big_separation / 2)), (360 * self.arc_c) + (self.big_separation / 2) + (self.offset * (self.smin + self.big_separation / 2)))

    # ----------------------------------------------------------------------
    def format_connectivities(self, connectivities):
        """"""
        if len(connectivities.shape) == 1:  # vector
            n = len(self.channels)
            tri = np.zeros((n, n))
            tri[np.triu_indices(n, 1)] = connectivities
            return tri

        return connectivities

    # ----------------------------------------------------------------------
    def connectivity(self, connectivities, threshold, min_alpha):
        """"""
        def map_(x, in_min, in_max, out_min, out_max):
            return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

        connectivities = self.format_connectivities(connectivities)

        chords = []
        for i, j in zip(*np.triu_indices(connectivities.shape[0])):

            if connectivities[i][j] < threshold:
                continue
            if i == j:
                continue

            kk = map_(connectivities[i][j], threshold, connectivities[connectivities != 1].max(), 1, self.smin / 2)

            w1 = (self.smin / 2) - kk * self.connection_width
            w2 = (self.smin / 2) + kk * self.connection_width

            x1, _ = self.get_level(self.arc_c)
            source = (self.channels[i], w1, w2, x1 - self.arcs_separation)
            destination = (self.channels[j], w1, w2, x1 - self.arcs_separation)

            chords.append([connectivities[i][j], source, destination])

        norm = matplotlib.colors.Normalize(vmin=threshold, vmax=connectivities[connectivities != 1].max())
        # norm2 = matplotlib.colors.Normalize(vmin=min_alpha, vmax=connectivities[connectivities != 1].max())

        for v_, src, des in sorted(chords):
            self.circle_.chord_plot(src, des,
                                    facecolor=matplotlib.pyplot.cm.get_cmap(self.arcs_cmap)(norm(v_), norm(v_)),
                                    edgecolor=matplotlib.pyplot.cm.get_cmap(self.arcs_cmap)(norm(v_), 1),
                                    linewidth=1,
                                    )

    # # ----------------------------------------------------------------------
    # @property
    # def figure(self):
        # """"""
        # return self.circle_.figure

    # ----------------------------------------------------------------------
    @property
    def circle(self):
        """"""
        return self.circle_

    # ----------------------------------------------------------------------
    def bitmap_topoplot(self, montage_name='standard_1005', resolution=64, interp='nearest', ax=None, head=False, contours=0):
        """"""
        info = mne.create_info(
            self.channels,
            sfreq=1,
            ch_types="eeg",
        )
        info.set_montage(montage_name)

        data = []
        for ch in self.channels:
            for area in self.areas:
                if ch in self.areas[area]:
                    data.append(list(self.areas.keys()).index(area))
                    continue

        if ax is None:
            ax = matplotlib.pyplot.subplot(111)

        matplotlib.rcParams['font.size'] = 18
        mne.viz.plot_topomap(data,
                             info,
                             axes=ax,
                             names=self.channels,
                             sensors=True,
                             show_names=True,
                             contours=contours,
                             cmap=self.areas_cmap,
                             outlines='skirt',
                             res=resolution,
                             extrapolate='head',
                             show=False,
                             image_interp=interp,

                             mask_params=dict(
                                 marker='o',
                                 markerfacecolor='#ffffff88',
                                 markeredgecolor='#000000',
                                 linewidth=0,
                                 markersize=self.markersize,
                                 zorder=3,
                             ),
                             mask=np.array([True] * len(self.channels)),

                             )

        # ax.set_xlim(-0.5, 0.5)

        return ax

    # ----------------------------------------------------------------------
    @property
    def figure(self):
        """"""
        plt.savefig('temp1.png')
        plt.close()

        plt.figure(figsize=(8, 8))
        self.bitmap_topoplot()
        plt.xlim(-0.15, 0.15)
        plt.savefig('temp2.png')
        plt.close()

        plt.figure(figsize=(20, 10), dpi=90)
        plt.subplots_adjust(wspace=0)
        plt.subplot(121)
        plt.imshow(plt.imread('temp1.png'))
        plt.axis('off')
        plt.subplot(122)
        plt.imshow(plt.imread('temp2.png'))
        plt.axis('off')

        return plt.gcf()
