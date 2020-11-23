import grid as gr
import random

# Globals

# Problem parameters
HUMIDITY = 0.0
LIGHTNING = 0.00002 #Probability of lightning
NEW_GROWTH = 0.002 #Probability of new growth
TREE_RATIO = 0.50 #Tree rate in the space
TREE_MAX_AGE = 10
RIVER = "line" # Shape of the river (line, sin)
RIVER_WIDTH = 2
CLOUDS = 20
COLOR_CLOUDS = (20, 20, 20)

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

def humidity_color():
    #(190,100,29) LIGHT
    #(82,46,13) DARK
    return (150 - HUMIDITY * 80, 100 - HUMIDITY * 54, 29 - HUMIDITY * 16)

def clouds_color(color: tuple):
    cloud = [color[i] - COLOR_CLOUDS[i] for i in range(3)]

    for i in range(len(cloud)):
        if cloud[i] < 0:
            cloud[i] = 0
    return tuple(cloud)
 
class Forest:

    # Grids
    _trees = None
    _burning = None
    _water = None
    _clouds = None
    
    # Element counts
    _tree = None
    _init = None
    _empties = None
    _burnt = None
    
    def __init__(self):
        
        # Grids needed to store burning and tree states of cells
        self._burning = gr.Grid()

        if RIVER is not None:
            self._water = gr.Grid(empty=False, river=RIVER, river_width=RIVER_WIDTH)
        else:
            self._water = gr.Grid()

        if CLOUDS is not None:
            clouds = self.generate_clouds(CLOUDS)
            self._clouds = gr.Grid(empty=False, clouds=clouds)
        else:
            self._clouds = gr.Grid()

        forbidden = [(x, y) for x in range(gr.nx) for y in range(gr.ny) if self._water[x,y] == 1]
        self._trees = gr.Grid(empty=False, ratio=TREE_RATIO, forbidden=forbidden)
        
        # Element counts 
        self._tree = gr.nx * gr.ny * TREE_RATIO
        self._init = self._tree
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

    def generate_clouds(self, n: int) -> list:
        clouds = []
        for k in range(n):
            x = random.randint(0, gr.nx - 1)
            y = random.randint(0, gr.ny - 1)
            w = random.randint(5, 15)
            h = random.randint(10, 20)

            for i in range(w):
                if i != 0 and i != w - 1:
                    clouds.append(((x + i) % gr.nx, (y - 1) % gr.ny))
                    clouds.append(((x + i) % gr.nx, (y + h) % gr.ny))
                for j in range(h):
                    clouds.append(((x + i) % gr.nx, (y + j) % gr.ny))
        return clouds   
    
    # Get state of a cell i.e (tree?, burning?, water?)
    def getCell(self, x: int, y: int) -> tuple:
        return (self._trees._gridbis[x, y], self._burning._gridbis[x, y],
                 self._water._gridbis[x, y], self._clouds._gridbis[x, y])
        
    # Tree igniting and age growing treatment
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
        if rnd_growth <= NEW_GROWTH * (1 + HUMIDITY * 10): 
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
            if self._burning[x, y] <= 0:
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

    def update_clouds(self):
        dxy = [(0, 0), (0, -1), (1, 0), (0, 1), (-1, 0)]
        dx = dxy[WIND][0] * WIND_STRENGTH
        dy = dxy[WIND][1] * WIND_STRENGTH

        for x in range(gr.nx):
            for y in range(gr.ny):
                self._clouds[(x + dx) % gr.nx, (y + dy) % gr.ny] = self._clouds._gridbis[x, y]


        self._clouds.updateBis()
                    


        


        
        
        
        
        
        
        
        
        

