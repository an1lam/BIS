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
    zone = Zone(20, 20, 20)
    # zone = Zone(7, 7, 1)
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

        self.grid = np.empty([height, width], dtype=np.object)
        for i in range(height):
            for j in range(width):
                self.grid[i][j] = Box()
        self.display_grid = np.zeros([height, width])

    def populate(self):
        # Initialize cells in this zone

        boxes = list(
            itertools.product(range(self.height), range(self.width)))
        random.shuffle(boxes)
        agent_boxes = boxes[:self.cell_count]
        for (x, y) in agent_boxes:
            self.grid[x][y].agents.append(agent.PC1())
            self.display_grid[x][y] = 1

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

                    for signal in new_signals:
                        new_grid[(i + x) % self.height][(j + y) % self.width].signals[signal] += new_signals[signal]

        self.grid = new_grid
        self.display_grid = new_display_grid

    def diffuse(self):
        """
        Update signal levels after diffusion.
        """
        new_grid = np.empty([self.height, self.width], dtype=np.object)
        for i in range(self.height):
            for j in range(self.width):
                new_grid[i][j] = Box()

        for i in xrange(self.height):
            for j in xrange(self.width):
                for signal in self.grid[i][j].signals:
                    new_grid[i][j].signals[signal] = self.calc_diffuse(signal, i, j)
                
                new_grid[i][j].agents = self.grid[i][j].agents
        
        self.grid = new_grid

    def calc_diffuse(self, signal, i, j):
        """
        Compute new level of a signal in a cell after diffusion
        """
        curr_val = self.grid[i][j].signals[signal]
        return (EvapRate * (curr_val +
                DiffusionConstant * (self.nAvg(signal, i, j) - curr_val)))
    
    def nAvg(self, signal, i, j):
        """
        Compute the average value of a signal in a cell's Moore neighborhood
        """
        nhood = self.neighborhood(i, j)
        return np.mean([box.signals[signal] for box in nhood])

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

    def signal_values(self, signal):
        return np.array([[self.grid[i][j].signals[signal] 
                          for j in xrange(self.width)]
                         for i in xrange(self.height)])

    def plot_signal(self, signal):
        fig = plt.figure()
        ax = plt.axes()
        mat = ax.matshow(self.signal_values(signal))
        plt.show()

    def signal_display(self, signal):
        return np.apply_along_axis(lambda x: x / 100, 0, self.signal_values(signal))

    def animate(self):
        fig, (agent_ax, signal_ax) = plt.subplots(1, 2, sharey=True)

        agent_ax.set_ylim(0, self.grid.shape[0])
        agent_ax.set_xlim(0, self.grid.shape[1])
        signal_ax.set_ylim(0, self.grid.shape[0])
        signal_ax.set_xlim(0, self.grid.shape[1])

        agent_mat = agent_ax.matshow(self.display_grid,
                                     vmin=0, vmax=10)
        signal_mat = signal_ax.matshow(self.signal_display(PK1),
                                       vmin=0, vmax=20)
        fig.colorbar(signal_mat)

        def anim_update(tick):
            self.update()
            self.diffuse()
            agent_mat.set_data(self.display_grid)
            signal_mat.set_data(self.signal_display(PK1))
            return agent_mat, signal_mat

        anim = animation.FuncAnimation(fig, anim_update, frames=100,
                                       interval=500, blit=False)
        anim.save('test.mp4', fps=5, extra_args=['-vcodec', 'libx264'])


def main():
    zone = Zone(6, 5, 3)
    zone.populate()
    zone.plot()


if __name__ == "__main__":
    main()
