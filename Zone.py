import copy
import itertools
import random
import numpy as np
import matplotlib.pyplot as plt
import agent

class Zone:
    def __init__(self, width, height, cell_count):
        self.width = width
        self.height = height
        self.cell_count = cell_count
        self.grid = [[[] for i in range(height)] for i in range(width)]

    def populate(self):
        # Initialize cells in this zone
        boxes = list(
            itertools.product(range(self.width),range(self.height)))
        random.shuffle(boxes)
        agent_boxes = boxes[:self.cell_count]
        for (x,y) in agent_boxes:
            self.grid[x][y].append(agent.Agent())

    def plot(self):
        fig, ax = plt.subplots()
        agent_colors = {1:'b'}

        print(self.grid)
        for (i, column) in enumerate(self.grid):
            for (j, box) in enumerate(column):
                if len(box) > 0:
                    print((i,j))
                    ax.scatter(
                        i+.5, j+0.5,
                        color=agent_colors[1])

        ax.set_title("Test", fontsize=10, fontweight='bold')
        ax.set_xlim([0, self.width])
        ax.set_ylim([0, self.height])
        ax.set_xticks([])
        ax.set_yticks([])
        plt.savefig("test")

def main():
    zone = Zone(6, 5, 3)
    zone.populate()
    zone.plot()


if __name__ == "__main__":
    main()
