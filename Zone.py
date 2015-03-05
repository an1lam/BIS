#!/usr/bin/env python

import copy
import itertools
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
import agent


class Box:
    def __init__(self):
        self.agents = []
        self.signals = []

class Zone:
    def __init__(self, width, height, cell_count):
        self.width = width
        self.height = height
        self.cell_count = cell_count
        self.grid = [[Box() for i in range(height)] for i in range(width)]
        self.display_grid = [[0 for i in range(height)] for i in range(width)]

    def populate(self):
        # Initialize cells in this zone
        boxes = list(
            itertools.product(range(self.width), range(self.height)))
        random.shuffle(boxes)
        agent_boxes = boxes[:self.cell_count]
        for (x, y) in agent_boxes:
            self.grid[x][y].agents.append(agent.Agent())
            self.display_grid[x][y] = 1

    def update(self):
        pass

    # rename to animate
    def plot(self):
        fig, ax = plt.subplots()
        agent_colors = {1: 'b'}

        print(self.grid)
        for (i, column) in enumerate(self.grid):
            for (j, box) in enumerate(column):
                if len(box.agents) > 0:
                    print((i, j))
                    ax.scatter(
                        i+.5, j+0.5,
                        color=agent_colors[1])

        ax.set_title("Test", fontsize=10, fontweight='bold')
        ax.set_xlim([0, self.width])
        ax.set_ylim([0, self.height])
        ax.set_xticks([])
        ax.set_yticks([])
        plt.savefig("test")

    def animate(self):
        fig = plt.figure()
        ax = plt.axes(xlim=(0, self.width), ylim=(0, self.height))
        print self.display_grid
        mat = ax.matshow(self.display_grid)

        def anim_update(tick):
            self.update()
            mat.set_data(self.display_grid)
            return mat,

        anim = animation.FuncAnimation(fig, anim_update, frames=200,
                                       interval=20)
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
