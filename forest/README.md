# Forest Fire project
Authors: [Germon Paul](https://github.com/pgermon) and [Chataigner Johan](https://github.com/JohanChataigne)

## Introduction

![Forest fire simulation with pygame](images/screen.png)

### Planes

The data representation of the forest is implemented by 3 planes:

First plane indicates the presence of a tree: 1-10 = tree age, 0 = empty  
Second plane indicates whether a tree is burning: 1-10 = burning time, 0 = not burning
Third plane indicates the presence of water: 1 = water, 0 = empty  

The forest is initialized with a certain ratio of the space occupied by trees of random age.

### Evolution rules

The evolution rules are as follows:

1.  A fully burnt tree turns into an empty cell.
2.  A non-burning tree can turn into a burning tree with probability depending on its number of neighbors burning and humidity rate.
3.  A burning tree can stop burning depending on the humidity rate.
4.  A tree with no burning neighbour ignites with a certain probability due to lightning.
5.  An empty space grows a new tree with a certain probability depending on the humidity rate.
6.  A tree grows older at each iteration (1-10).
7.  The older a tree, the more steps it takes to burn.
8.  Fire can't spread in the opposite wind's direction.
9.  The stronger the wind, the further the fire can spread.
10.  Trees can't grow in water: water stops fire, except if the wind is strong enough.

## Pygame interface

![Pygame interface](images/interface.png)

## Files and folders

- grid.py: implements data structures for a plane
- forest.py: implements interactions between the different elements of the forest (trees, fire, wind, water)
- scene.py: handles the display of the simulation with pygame
- input_box.py: implements input boxes
- input_button.py: implements input buttons
- percolation.py: runs a script to compute the percolation threshold
- ./images: folder which contains the images generated

## Run commands

- Run simulation with `make`
- Run percolation computation with `make percolation`
