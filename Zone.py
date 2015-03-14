#!/usr/bin/env python


from __future__ import division
import pdb
import copy
import itertools
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib import gridspec
import agent
from BIS_constants import *

def test(width=20, height=20, num_cells=10, fname=None):
    # zone = Zone(20, 20, 20)
    zone = Zone(width, height, num_cells)
    zone.populate()
    zone.animate(fname)

class Box:
    def __init__(self):
        self.agents = {
            PC_agt: [],
            MP_agt: [],
            NK_agt: [],
        }
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

        mid_i = int(height / 2)
        mid_j = int(width / 2)
        self.grid[mid_i][mid_j].signals[virus] = 50

    def populate(self):
        # Initialize cells in this zone

        boxes = list(
            itertools.product(range(self.height), range(self.width)))
        random.shuffle(boxes)
        agent_boxes = boxes[:self.cell_count]
        # for (x, y) in agent_boxes:
        mid_x = int(self.width/2)
        for x in xrange(self.width):
            for y in [0, 1, mid_x, mid_x+1]:
                self.grid[x][y].agents[PC_agt].append(agent.PC1())

        mid_y = int(self.height/2)
        for y in xrange(self.height):
            for x in [0, 1, mid_y, mid_y + 1]:
                if not self.grid[x][y].agents[PC_agt]:
                    self.grid[x][y].agents[PC_agt].append(agent.PC1())

        self.grid[mid_x][mid_y].agents[PC_agt][0].current_state = 3 
            
        for x, y in [(0, 0), (int(self.width/2), int(self.height/2))]:
            self.grid[x][y].agents[PC_agt].append(agent.PC1())

        for (x, y) in boxes[self.cell_count:2*self.cell_count]:
            self.grid[x][y].agents[MP_agt].append(agent.MP())

        for (x, y) in boxes[2*self.cell_count:3*self.cell_count]:
            self.grid[x][y].agents[NK_agt].append(agent.NK())

    def update(self):
        new_grid = np.empty([self.height, self.width], dtype=np.object)
        for i in range(self.height):
            for j in range(self.width):
                new_grid[i][j] = Box()
                new_grid[i][j].signals = self.grid[i][j].signals

        for i in xrange(self.height):
            for j in xrange(self.width):
                for agt_type in self.grid[i][j].agents.keys():
                    for agt in self.grid[i][j].agents[agt_type]:
                        agt.probe(self.neighborhood(i, j))

        for i in xrange(self.height):
            for j in xrange(self.width):
                for agt_type in self.grid[i][j].agents.keys():
                    for agt in self.grid[i][j].agents[agt_type]:
                        x, y = agt.move()
                        agt.update()
                        new_grid[(i + x) % self.height][(j + y) % self.width].agents[agt_type].append(agt)
                        new_signals = agt.emit()

                        for signal in new_signals:
                            new_grid[(i + x) % self.height][(j + y) % self.width].signals[signal] += new_signals[signal]

        self.grid = new_grid

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
        return np.apply_along_axis(lambda x: x / 10, 0, self.signal_values(signal))

    def display_grid(self):
        vals = {
            'livePC': 1,
            'infectedPC': 9,
            'deadPC': 10,
            MP1: 4,
            MP2: 5,
            MP0: 6,
            NK_agt: 8
        }

        display = np.zeros([self.height, self.width])
        for i in xrange(self.height):
            for j in xrange(self.width):
                if len(self.grid[i][j].agents[MP_agt]) > 0:
                    display[i][j] = vals[self.grid[i][j].agents[MP_agt][0].kind]
                elif len(self.grid[i][j].agents[PC_agt]) > 0:
                    if self.grid[i][j].agents[PC_agt][0].alive():
                        display[i][j] = vals['livePC']
                    if self.grid[i][j].agents[PC_agt][0].infected():
                        display[i][j] = vals['infectedPC']
                    if not self.grid[i][j].agents[PC_agt][0].alive():
                        display[i][j] = vals['deadPC']
                elif len(self.grid[i][j].agents[NK_agt]) > 0:
                    display[i][j] = vals[NK_agt]



        # TODO: account for stacked agents
        return display

    def animate(self, fname=None, frames=100):
        # fig, (agent_ax, signal_ax) = plt.subplots(1, 2, sharey=True)
        fig, (agent_ax, signal_ax) = plt.subplots(1, 2)

        fig = plt.figure()
        gs = gridspec.GridSpec(1, 2, width_ratios=[1,1.26])
        agent_ax = plt.subplot(gs[0])
        signal_ax = plt.subplot(gs[1])

        agent_ax.set_ylim(-0.5, self.grid.shape[0] - 0.5)
        agent_ax.set_xlim(-0.5, self.grid.shape[1] - 0.5)
        signal_ax.set_ylim(-0.5, self.grid.shape[0] - 0.5)
        signal_ax.set_xlim(-0.5, self.grid.shape[1] - 0.5)

        agent_mat = agent_ax.imshow(self.display_grid(),
                                    vmin=0, vmax=10, aspect='equal',
                                    interpolation='nearest', origin='upper')
        signal_mat = signal_ax.imshow(self.signal_display(virus),
                                      vmin=0, vmax=20, aspect='equal',
                                      interpolation='nearest', origin='upper')
        fig.colorbar(signal_mat, shrink=.5)

        def anim_update(tick):
            # print tick
            self.update()
            self.diffuse()
            agent_mat.set_data(self.display_grid())
            signal_mat.set_data(self.signal_display(virus))
            return agent_mat, signal_mat

        if fname:
            interval = 100
        else:
            interval = 3000
        anim = animation.FuncAnimation(fig, anim_update, frames=frames,
                                       interval=interval, blit=False)

        if fname:
            anim.save(fname, fps=3, extra_args=['-vcodec', 'libx264'])
        else:
            plt.show()


def main():
    zone = Zone(6, 5, 3)
    zone.populate()
    zone.plot()


if __name__ == "__main__":
    main()
