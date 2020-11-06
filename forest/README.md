# Forest Fire project

## Introduction

![Forest fire simulation with pygame][./images/screen.png]

### Planes

Plane 0 indicates the presence of a tree: 1 = tree, 0 = empty, 2-10 = old tree  
Plane 1 indicates whether a tree is burning: 1 = burning, 0 = not burning, 2-10 = burning time (just visual data)  
Plane 2 indicates the presence of water: 1 = water, 0 = empty  

The forest is initialized with 'tree_ratio'% of the space occupied by trees of random age.

### Rules

The transition rules are as follows.

1.  A burning tree turns into an empty cell.
2.  A non-burning tree with one burning neighbour turns into a burning tree.
3.  A tree with no burning neighbour ignites with probability 'lightning' due to lightning.
4.  An empty space grows a new tree with probability 'new_growth'.
5.  An old tree takes more steps to burn. (1 per year)
6.  Fire can only spread in the wind's direction (North = 1, East = 2, South = 3, West = 4).
7.  The fire spreads further if the wind is stronger
8.   Water stops fire, except if the wind is strong enough...

## Files and folders

- grid.py: implements data structures for a plane
- forest.py: implements interactions between the different elements of the forest (trees, fire, wind, water)
- scene.py: handles the display of the simulation with pygame
- input_box.py: implements input boxes
- input_button.py: implements input buttons
- percolation.py: runs a script to compute the percolation threshold
- ./results: folder which contains the images generated

## Run commands

- python3 ./scene.py
- python3 ./percolation.py