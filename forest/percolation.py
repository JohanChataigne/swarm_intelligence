import sys, math, random
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import forest as ft

if __name__ == '__main__':

    ft.LIGHTNING = 0
    ft.NEW_GROWTH = 0
    ft.WIND = 1
    ft.WIND_STRENGTH = 1
    ft.RIVER = None
    ft.CLOUDS = None

    densities = [d for d in np.arange(0.01, 1, 0.01)]
    percentageBurnt = []

    for density in densities:
        ft.TREE_RATIO = density
        forest = ft.Forest()

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
    plt.savefig("./images/percolation.png")