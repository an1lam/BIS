#!/usr/bin/env python


from __future__ import division
import pdb
import copy
import itertools
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
import agent
from BIS_constants import *

def test():
    # zone = Zone(20, 20, 40)
    zone = Zone(7, 7, 1)
    zone.populate()
    zone.animate()

class Box:
    def __init__(self):
        self.agents = []
        self.signals = {
            PK1: 0,
            virus: 0,
            apop: 0,
            necro: 0,
            MK1: 0,
            MK2: 0,
            CK1: 0,
            CK2: 0,
            Ab1: 0,
            Ab2: 0,
            comp: 0,
            G1: 0
        }

    def update(signals):
        for signal in signals.keys():
            self.signals[signal] += signals[signal]

    def __repr__(self):
        return "%s\n%s" % (repr(self.agents), repr(self.signals))


class Zone:
    def __init__(self, width, height, cell_count):
        self.width = width
        self.height = height
        self.cell_count = cell_count
        # self.grid = [[Box() for i in range(width)] for j in range(height)]
        # self.display_grid = [[0 for i in range(width)] for j in range(height)]
        # self.signal_display = [[0 for i in range(width)] for j in range(height)]

        self.grid = np.empty([height, width], dtype=np.object)
        for i in range(height):
            for j in range(width):
                self.grid[i][j] = Box()
        self.display_grid = np.zeros([height, width])
        self.signal_display = np.zeros([height, width])


    def populate(self):
        # Initialize cells in this zone

        boxes = list(
            itertools.product(range(self.height), range(self.width)))
        random.shuffle(boxes)
        agent_boxes = boxes[:self.cell_count]
        for (x, y) in agent_boxes:
            self.grid[x][y].agents.append(agent.PC1())
            self.display_grid[x][y] = 1

    def signal_values(self, signal):
        return np.array([[self.grid[i][j].signals[signal] for j in xrange(self.width)] for i in xrange(self.height)])
        # vals = np.zeros([self.height, self.width])
        # for i in xrange(self.height):
            # for j in xrange(self.

    def neighborhood(self, i, j):
        """
        Return Moore neighborhood of a Zone entry.

        Arguments
        ---------
        i (int)
        j (int)

        Returns
        -------
        neighborhood (np.ndarray(9,))
        """
        roll1 = np.roll(self.grid, self.grid.shape[0] - i + 1, axis=0)
        roll2 = np.roll(roll1, self.grid.shape[1] - j + 1, axis=1)
        return roll2[0:3, 0:3].flatten()

    def nAvg(self, signal, i, j):
        nhood = self.neighborhood(i, j)
        return np.mean([box.signals[signal] for box in nhood])

    def diffuse(self):

        new_grid = np.empty([self.height, self.width], dtype=np.object)
        for i in range(self.height):
            for j in range(self.width):
                new_grid[i][j] = Box()

        # pdb.set_trace()
        for i in xrange(self.height):
            for j in xrange(self.width):
                for signal in self.grid[i][j].signals:
                    curr_val = self.grid[i][j].signals[signal]
                    new_val = EvapRate * (curr_val + DiffusionConstant * (self.nAvg(signal, i, j) - curr_val))
                    new_grid[i][j].signals[signal] = new_val
                    if signal == PK1:
                        self.signal_display[i][j] = new_val
                new_grid[i][j].agents = self.grid[i][j].agents
        # pdb.set_trace()
        self.grid = new_grid


    def update(self):

        new_grid = np.empty([self.height, self.width], dtype=np.object)
        for i in range(self.height):
            for j in range(self.width):
                new_grid[i][j] = Box()
                for signal in new_grid[i][j].signals:
                    new_grid[i][j].signals[signal] = self.grid[i][j].signals[signal]
        
        new_display_grid = np.zeros([self.height, self.width])
        for i in xrange(self.height):
            for j in xrange(self.width):
                for agt in self.grid[i][j].agents:
                    x, y = agt.probe([])  # TODO: pass surrounding boxes
                    new_grid[(i + x) % self.height][(j + y) % self.width].agents.append(agt)
                    new_display_grid[(i + x) % self.height][(j + y) % self.width] = 1  # TODO: use agent type number instead
                                                        # TODO: account for stacked agents
                    new_signals = agt.emit()
                    # pdb.set_trace()

                    # FIX: add new_signal to old grid value not new grid
                    for signal in new_signals:
                        new_grid[(i + x) % self.height][(j + y) % self.width].signals[signal] += new_signals[signal]

        # pdb.set_trace()
        self.grid = new_grid
        self.display_grid = new_display_grid


    # rename to animate
    # def plot(self):
    #     fig, ax = plt.subplots()
    #     agent_colors = {1: 'b'}

    #     print(self.grid)
    #     for (i, column) in enumerate(self.grid):
    #         for (j, box) in enumerate(column):
    #             if len(box.agents) > 0:
    #                 print((i, j))
    #                 ax.scatter(
    #                     i+.5, j+0.5,
    #                     color=agent_colors[1])

    #     ax.set_title("Test", fontsize=10, fontweight='bold')
    #     ax.set_xlim([0, self.width])
    #     ax.set_ylim([0, self.height])
    #     ax.set_xticks([])
    #     ax.set_yticks([])
    #     plt.savefig("test")

    def plot_signal(self, signal):
        fig = plt.figure()
        ax = plt.axes()
        mat = ax.matshow(self.signal_values(signal))
        plt.show()

    
    def animate(self):
        # pdb.set_trace()
        fig = plt.figure()
        # ax = plt.axes(xlim=(0, self.width), ylim=(0, self.height))
        ax = plt.axes()
        # print type(self.display_grid)
        # print type(self.signal_values(PK1))
        # mat = ax.matshow(self.display_grid)
        # mat = ax.matshow(self.signal_values(PK1))
        mat = ax.matshow(np.apply_along_axis(lambda x: x / 100, 0, self.signal_values(PK1)), vmin=0, vmax=10)
        fig.colorbar(mat)

        # sig = np.array([[ 110., 110., 220., 220.],
                        # [ 220., 220., 220., 330.],
                        # [ 220., 220., 220., 330.],
                        # [ 110., 110.,   0., 110.]])

        # sig = np.array([[2, 1, 0], [0, 1, 0]])
        # mat = ax.matshow(sig)

        # fig, (agent_ax, signal_ax) = plt.subplots(1, 2, sharey=True)
        # agent_mat = agent_ax.matshow(self.display_grid)
        # signal_mat = signal_ax.matshow(self.signal_display)
        # pdb.set_trace()

        def anim_update(tick):
            self.update()
            self.diffuse()
            # mat.set_data(self.display_grid)
            # print self.signal_values(PK1)
            print np.apply_along_axis(lambda x: x / 100, 0, self.signal_values(PK1))
            # mat.set_data(self.signal_values(PK1))
            mat.set_data(np.apply_along_axis(lambda x: x / 100, 0, self.signal_values(PK1)))
            # for i in xrange(sig.shape[0]):
                # for j in xrange(sig.shape[1]):
                    # # sig[i][j] = int(not sig[i][j])
                    # sig[i][j] = random.randint(200, 1100)
            # print sig
            # mat.set_data(sig)
            # signal_mat.set_data(self.signal_display)
            # return agent_mat, signal_mat
            return mat, 

        anim = animation.FuncAnimation(fig, anim_update, frames=1,
                                       interval=3000, blit=False)
        anim.save('test.mp4', fps=30, extra_args=['-vcodec', 'libx264'])
        plt.show()

    # def show(self):
    #
    #     scatter = ax.scatter([], [])

    #     def init():
    #         scatter.set_paths([], [])
    #         return scatter,

    #     def animate(tick):
    #         agent_colors = {1: 'b'}
    #         for (i, column) in enumerate(self.grid):
    #             for (j, box) in enumerate(column):
    #                 if len(box.agents) > 0:
    #                     print((i, j))
    #                     scatter.set_paths(
    #                         i+.5, j+0.5,
    #                         color=agent_colors[1])
    #         return scatter,

    #     anim = animation.FuncAnimation(fig, animate, init_func=init,
    #                                    frames=200, interval=20, blit=True)
    #     anim.save('test.mp4', fps=30, extra_args=['-vcodec', 'libx264'])

    #     plt.show()


def main():
    zone = Zone(6, 5, 3)
    zone.populate()
    zone.plot()


if __name__ == "__main__":
    main()
