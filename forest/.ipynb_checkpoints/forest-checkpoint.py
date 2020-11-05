import grid as gr
import random

# Globals

# Problem parmeters
LIGHTNING = 0.00002 #Probability of lightning
NEW_GROWTH = 0.002 #Probability of new growth
TREE_RATIO = 0.50 #Tree rate in the space
RIVER = True
LAKES = 0

# Map winds with their opposite direction (sense, direction, label)
WINDS = {
    0 : (0, 0, "No wind"),
    1 : (1, -1, "North"), #(0, 1)
    2 : (0, 1, "East"),  #(1, 0)
    3 : (1, 1, "South"),  #(0, -1)
    4 : (0, -1, "West")  #(-1, 0)
}

# Wind direction for our forest
WIND = 0
# Wind strength (0-3)
WIND_STRENGTH = 0

'''
                    Forest Fire

        Plane 0 indicates the presence of a tree:
            1 = tree, 0 = empty, 2 = old tree
        Plane 1 indicates whether a tree is burning:
            1 = burning, 0 = not burning

        The forest is initialized with 'tree_ratio'% of the space occupied by trees.
        
        The transition rules are as follows.

        1.  A burning tree turns into an empty cell.
        2.  A non-burning tree with one burning neighbour turns
            into a burning tree.
        3.  A tree with no burning neighbour ignites with
            probability 'lightning' due to lightning.
        4.  An empty space grows a new tree with probability 'new_growth'.
        5.  An old tree takes 2 steps to burn.
        6.  Fire can only spread in the wind's direction (North = 1, East = 2, South = 3, West = 4).
        7.  The fire spreads further if the wind is stronger
        8   Water stops fire, except if the wind is strong enough...

'''
 
class Forest:

    # Grids
    _trees = None
    _burning = None
    
    # Element counts
    _old = None
    _young = None
    _init = None
    _empties = None
    _burnt = None
    
    def __init__(self, gridTrees, gridBurning):
        
        # Grids needed to store burning and tree states of cells
        self._trees = gridTrees
        self._burning = gridBurning
        
        # Element counts 
        self._old = 0
        self._young = gr.nx * gr.ny * TREE_RATIO
        self._init = self._young
        self._empties = gr.nx * gr.ny * (1-TREE_RATIO)

        # If no lightning probability, one tree ignites at the beginning (usefull for percolation)
        if LIGHTNING == 0:
            bx = random.randint(0, gr.nx - 1)
            by = random.randint(0, gr.ny - 1)
            while self._trees[bx, by] == 0:
                bx = random.randint(0, gr.nx - 1)
                by = random.randint(0, gr.ny - 1)
            self._burning[bx, by] = 1
            self._burning._gridbis[bx, by] = 1
            self._burnt = 1
        else:
            self._burnt = 0
        
    # Get state of a tree i.e (tree?, burning?)
    def getTree(self, x, y):
        return (self._trees._gridbis[x, y], self._burning._gridbis[x, y])
        
    # Tree igniting treatment
    def ignite_grow(self, x, y):

        self._burning.resetIndexVoisins()
        if WIND > 0 and WIND_STRENGTH > 0:
            v = WINDS[WIND]
            self._burning._indexVoisins = [ w for w in self._burning._indexVoisins if w[v[0]] != v[1]]
            neighbours = self._burning.furtherNeighbours(x, y, WIND_STRENGTH)
            
        else:
            neighbours = self._burning.voisins(x, y)

        # Case at least one neighbour is burning
        if 1 in neighbours:
            self._burning[x, y] = 1
            self._burnt += 1

        # Ignite due to lightning
        else:           
            rnd_ignite = random.random()
            if rnd_ignite <= LIGHTNING: 
                self._burning[x, y] = 1 
                self._burnt += 1
            else: 
                self._burning[x, y] = 0
                
                if self._trees._gridbis[x, y] < 2:
                    self._trees[x, y] += 1
                    self._old += 1
                    self._young -= 1
    
    # Growing treatment 
    def grow(self, x, y):
        rnd_growth = random.random()
        if rnd_growth <= NEW_GROWTH: 
            self._trees[x, y] = 1 
            self._young += 1
            self._empties -= 1
    
    # Make a tree die (reset cell) or make it grow if its strong enough
    def die(self, x, y):
        # Tree is not fully burnt
        if self._trees._gridbis[x, y] > 1:
            self._trees[x, y] -= 1
            self._old -= 1
            self._young += 1
        
        # Tree dies from burning
        else:
            self._trees[x, y] = 0
            self._burning[x, y] = 0
            self._burnt -= 1
            self._young -= 1
            self._empties += 1
    
    # Update forest
    def update(self):
        
        for x in range(gr.nx):
            for y in range(gr.ny):
                
                cell = self.getTree(x, y)
                
                # Treatment for a cell with a tree
                if cell[0]:
                    
                    # Each burning tree turns into an empty cell
                    if cell[1]:
                        self.die(x, y)

                    # Otherwize update tree burning state or age(check neighbours)
                    else:
                        self.ignite_grow(x, y)
                
                # Treatment of empty cell
                else:
                    self.grow(x, y)
        
        #Update copies
        self._trees.updateBis()
        self._burning.updateBis()
                    


        


        
        
        
        
        
        
        
        
        

