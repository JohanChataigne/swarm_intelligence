import numpy as np
import random
import math

# Globals
__gridSize__ = (900,900) 
__cellSize__ = 10
__gridDim__ = tuple(map(lambda x: int(x/__cellSize__), __gridSize__))
nx, ny = __gridDim__

class Grid:
    _grid = None
    _gridbis = None
    _indexVoisins = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    
    def __init__(self, empty=True, ratio=None, river=None, river_width=3, forbidden=None, clouds=None):
        
        # Create an empty grid
        if empty:
            self._grid = np.zeros(__gridDim__, dtype='int8')
            self._gridbis = np.zeros(__gridDim__, dtype='int8')
            
        # Create a grid with one horizontal river of river_width at y0
        elif river is not None:
            self._grid = np.zeros(__gridDim__, dtype='int8')
            self._gridbis = np.zeros(__gridDim__, dtype='int8')
            
            y0 = np.random.randint(25, 66)
            
            for x in range(nx):
                for y in range(river_width):

                    if river == "line":
                        self._grid[x, y0 + y] = 1
                    elif river == "sin":
                        self._grid[x, int(y0 + y + math.sin(x))] = 1

        elif clouds is not None:
            self._grid = np.zeros(__gridDim__, dtype='int8')

            for x, y in clouds:
                self._grid[x, y] = 1
        
        # Fill grid available space with ratio*size random values (from 1 to 10)
        else:
            assert(ratio is not None)
            size = nx * ny             
            self._grid = np.random.randint(1, 11, size)
            self._grid[:int((1-ratio)*size)] = 0
            np.random.shuffle(self._grid)
            self._gridbis = np.reshape(self._grid, (nx, ny))
            self._grid = np.reshape(self._grid, (nx, ny))
            
            if forbidden is not None:
                for (x, y) in forbidden:
                    self._grid[x, y] = 0
                
                # Free allowed positions in the grid according to the forbidden positions
                allowed_free = [(x,y) for x in range(nx) for y in range(ny) if (x,y) not in forbidden
                                                                                    and self._grid[x,y] == 0]
                
                for i in range(len(forbidden)):
                    rnd_x, rnd_y = allowed_free[np.random.randint(0, len(allowed_free))]
                    self._grid[rnd_x, rnd_y] = 1
                
        self._gridbis = self._grid
                
        assert (np.array_equal(self._grid, self._gridbis))

    def resetIndexVoisins(self):
        self._indexVoisins = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

    def indiceVoisins(self, x: int, y: int) -> list:
        return [(dx+x,dy+y) for (dx,dy) in self._indexVoisins if dx+x >=0 and dx+x < __gridDim__[0] and dy+y>=0 
                                                                        and dy+y < __gridDim__[1]] 

    def voisins(self,x: int, y: int) -> list:
        return [self._gridbis[vx,vy] for (vx,vy) in self.indiceVoisins(x,y)]
    
    # Returns the list of neighbours of the cell (x, y) depending on the wind strength ws
    def furtherNeighbours(self, x: int, y: int, ws: int) -> list:
        neighbours = self.indiceVoisins(x, y)
        further_neighbours = neighbours.copy()
        
        for k in range(ws-1):
            tmp_neighbours = [self.indiceVoisins(xbis, ybis) for (xbis, ybis) in neighbours]
            tmp_neighbours = sum(tmp_neighbours, []) #Flatten the list 
            further_neighbours += tmp_neighbours
            further_neighbours = list(set(further_neighbours)) #Unique values
            neighbours = tmp_neighbours.copy()
            
        return [self._gridbis[vx, vy] for (vx, vy) in further_neighbours]
 
   
    def sommeVoisins(self, x: int, y: int) -> int:
        return sum(self.voisins(x,y))

    def sumEnumerate(self) -> list:
        return [(c, self.sommeVoisins(c[0], c[1])) for c, _ in np.ndenumerate(self._grid)]

    def drawMe(self):
        pass
    
    def updateBis(self):
        self._gridbis = np.copy(self._grid)
    
    def __getitem__(self, key: tuple):
        return self._grid[key[0], key[1]]
    
    def __setitem__(self, key: tuple, value: int):
        self._grid[key[0], key[1]] = value