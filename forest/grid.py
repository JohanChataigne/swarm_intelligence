import numpy as np
import random

# Globals
__gridSize__ = (900,900) 
__cellSize__ = 10 
__gridDim__ = tuple(map(lambda x: int(x/__cellSize__), __gridSize__))
nx, ny = __gridDim__

class Grid:
    _grid = None
    _gridbis = None
    _indexVoisins = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    
    def __init__(self, empty=True, ratio=None, circles=0, line=False):
        
        if empty:
            self._grid = np.zeros(__gridDim__, dtype='int8')
            self._gridbis = np.zeros(__gridDim__, dtype='int8')
        else:
            assert(ratio is not None)
            size = __gridDim__[0] * __gridDim__[1]
            self._grid = np.random.randint(1, 11, size)
            self._grid[:int((1-ratio)*size)] = 0
            np.random.shuffle(self._grid)
            self._gridbis = np.reshape(self._grid, (__gridDim__[0], __gridDim__[1]))
            self._grid = np.reshape(self._grid, (__gridDim__[0], __gridDim__[1]))
        
        assert (np.array_equal(self._grid, self._gridbis))
        nx, ny = __gridDim__

    def resetIndexVoisins(self):
        self._indexVoisins = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

    def indiceVoisins(self, x,y):
        return [(dx+x,dy+y) for (dx,dy) in self._indexVoisins if dx+x >=0 and dx+x < __gridDim__[0] and dy+y>=0 and dy+y < __gridDim__[1]] 

    def voisins(self,x,y):
        return [self._gridbis[vx,vy] for (vx,vy) in self.indiceVoisins(x,y)]
    
    def furtherNeighbours(self, x, y, ws):
        neighbours = self.indiceVoisins(x, y)
        further_neighbours = neighbours.copy()
        
        for k in range(ws-1):
            tmp_neighbours = [self.indiceVoisins(xbis, ybis) for (xbis, ybis) in neighbours]
            tmp_neighbours = sum(tmp_neighbours, []) #Flatten the list 
            further_neighbours += tmp_neighbours
            further_neighbours = list(set(further_neighbours)) #Uniq values
            neighbours = tmp_neighbours.copy()
            

        return [self._gridbis[vx, vy] for (vx, vy) in further_neighbours]
 
   
    def sommeVoisins(self, x, y):
        return sum(self.voisins(x,y))

    def sumEnumerate(self):
        return [(c, self.sommeVoisins(c[0], c[1])) for c, _ in np.ndenumerate(self._grid)]

    def drawMe(self):
        pass
    
    def updateBis(self):
        self._gridbis = np.copy(self._grid)
    
    def __getitem__(self, key):
        return self._grid[key[0], key[1]]
    
    def __setitem__(self, key, value):
        self._grid[key[0], key[1]] = value