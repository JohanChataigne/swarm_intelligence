import sys, math, random
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import forest as ft

if __name__ == '__main__':

    ft.lightning = 0
    ft.new_growth = 0
    ft.WIND = 0
    ft.WIND_STRENGTH = 0

    densities = [d for d in np.arange(0.01, 1, 0.01)]
    percentageBurnt = []

    for density in densities:
        ft.tree_ratio = density
        forest = ft.Forest(ft.gr.Grid(empty=False, ratio=density), ft.gr.Grid())

        done = False       
        while done == False:
            
            forest.update()

            if forest._burnt == 0:
                #print("No more burning trees")
                done = True
                continue

        perc = (1 - (forest._tree / forest._init)) * 100
        percentageBurnt.append(perc)
        print(f"For density {density:.2f}, {perc:.2f}% of the trees have burnt")

    plt.xlabel("Forest density")
    plt.ylabel("Percentage of trees burnt")
    plt.plot(densities, percentageBurnt)
    plt.show()
    plt.savefig("./results/percolation.png")