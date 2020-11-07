import grid as gr
import random

# Globals

# Problem parmeters
HUMIDITY = 1.0
LIGHTNING = 0.00002 #Probability of lightning
NEW_GROWTH = 0.002 #Probability of new growth
TREE_RATIO = 0.50 #Tree rate in the space
TREE_MAX_AGE = 10
RIVER = "line" # Shape of the river (line, sin)
RIVER_WIDTH = 2
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
# Wind strength (0-WIND_MAX)
WIND_STRENGTH = 0
WIND_MAX = 3

'''
                    Forest Fire

        Plane 0 indicates the presence of a tree:
            1 = tree, 0 = empty, 2-10 = old tree
        Plane 1 indicates whether a tree is burning:
            1 = burning, 0 = not burning, 2-10 = burning time (just visual data)

        The forest is initialized with 'tree_ratio'% of the space occupied by trees of random age.
        
        The transition rules are as follows.

        1.  A burning tree turns into an empty cell.
        2.  A non-burning tree with one burning neighbour turns
            into a burning tree.
        3.  A tree with no burning neighbour ignites with
            probability 'lightning' due to lightning.
        4.  An empty space grows a new tree with probability 'new_growth'.
        5.  An old tree takes more steps to burn. (1 per year)
        6.  Fire can only spread in the wind's direction (North = 1, East = 2, South = 3, West = 4).
        7.  The fire spreads further if the wind is stronger
        8   Water stops fire, except if the wind is strong enough...

'''

def humidity_color():
    #(181,101,29) LIGHT
    #(82,46,13) DARK
    return (190 - HUMIDITY * 108, 100 - HUMIDITY * 54, 29 - HUMIDITY * 16)
 
class Forest:

    # Grids
    _trees = None
    _burning = None
    _water = None
    
    # Element counts
    _tree = None
    _init = None
    _empties = None
    _burnt = None
    
    def __init__(self):#, gridWater):
        
        # Grids needed to store burning and tree states of cells
        self._burning = gr.Grid()
        self._water = gr.Grid(empty=False, river=RIVER, river_width=RIVER_WIDTH)
        forbidden = [(x, y) for x in range(gr.nx) for y in range(gr.ny) if self._water[x,y] == 1]
        self._trees = gr.Grid(empty=False, ratio=TREE_RATIO, forbidden=forbidden)
        
        # Element counts 
        self._tree = gr.nx * gr.ny * TREE_RATIO
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

     
    # Get state of a cell i.e (tree?, burning?, water?)
    def getCell(self, x: int, y: int) -> tuple:
        return (self._trees._gridbis[x, y], self._burning._gridbis[x, y], self._water._gridbis[x, y])
        
    # Tree igniting treatment
    def ignite_grow(self, x: int, y: int):

        # Computes the neighbours of the cell (x, y) depending on the wind
        self._burning.resetIndexVoisins()
        if WIND > 0 and WIND_STRENGTH > 0:
            v = WINDS[WIND]
            self._burning._indexVoisins = [ w for w in self._burning._indexVoisins if w[v[0]] != v[1]]
            neighbours = self._burning.furtherNeighbours(x, y, WIND_STRENGTH)
            
        else:
            neighbours = self._burning.voisins(x, y)

        # Ignites with a probability that depends on the number of neighbours burning and the humidity rate
        ignite_prob = (1 - HUMIDITY) * sum(neighbours) * 1.0/len(neighbours)
        rnd_ignite = random.random()
        if rnd_ignite < ignite_prob:
            self._burning[x, y] = 1
            self._burnt += 1

        else:          
            # Ignites due to lightning with a certain probability 
            rnd_ignite = random.random()
            if rnd_ignite <= LIGHTNING: 
                self._burning[x, y] = 1 
                self._burnt += 1
            else: 
                self._burning[x, y] = 0
                # Grows older if not at max age yet
                if self._trees._gridbis[x, y] < TREE_MAX_AGE:
                    self._trees[x, y] += 1
    
    # Growing treatment 
    def grow(self, x: int, y: int):
        # A new tree grows from empty cell with a probability depending on humidity rate
        rnd_growth = random.random()
        if rnd_growth <= NEW_GROWTH * (1 + HUMIDITY): 
            self._trees[x, y] = 1 
            self._tree += 1
            self._empties -= 1
    
    # Treatment for a burning tree: can stop burning, continue or die
    def burning_treatment(self, x: int, y: int):

        # Stops burning depending on the humidity rate
        rnd_stop = random.random()
        if rnd_stop <= HUMIDITY:
            self._burning[x, y] -= int(HUMIDITY * 10)

            # Stops burning
            if self._burning[x, y] < 0:
                self._burning[x, y] = 0
                self._burnt -= 1

        else:
            # Tree is not fully burnt
            if self._trees._gridbis[x, y] > 1:
                self._trees[x, y] -= 1
                self._burning[x, y] += 1
            
            # Tree dies from burning
            else:
                self._trees[x, y] = 0
                self._burning[x, y] = 0
                self._burnt -= 1
                self._tree -= 1
                self._empties += 1
    
    # Update forest
    def update(self):
        
        for x in range(gr.nx):
            for y in range(gr.ny):
                
                cell = self.getCell(x, y)

                # Treatment for cells not in water
                if not cell[2]:
                
                    # Treatment for a tree
                    if cell[0]:
                        
                        # Treatment for a burning tree: can stop burning, continue or die
                        if cell[1]:
                            self.burning_treatment(x, y)

                        # Treatment for a non-burning tree: can ignite or grow older
                        else:
                            self.ignite_grow(x, y)
                    
                    # Treatment for an empty cell: can grow a new tree
                    else:
                        self.grow(x, y)
        
        #Update copies
        self._trees.updateBis()
        self._burning.updateBis()
                    


        


        
        
        
        
        
        
        
        
        

