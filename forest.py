import sys, math, random
import pygame
import pygame.draw
import numpy as np

__screenSize__ = (1250,900)
__gridSize__ = (900,900) 
__cellSize__ = 10 
__gridDim__ = tuple(map(lambda x: int(x/__cellSize__), __gridSize__))
__density__ = 3 

__colors__ = [(255,255,255),(0,255,0),(0, 86, 27),(255,140,0)]

lightning = 0.00002 #Probability of lightning
new_growth = 0.002 #Probability of new growth
tree_ratio = 0.65 #Tree rate in the space

# Map winds with their opposite direction (sense, direction, label)
winds = {
    1 : (1, -1, "North"), #(0, 1)
    2 : (0, 1, "East"),  #(1, 0)
    3 : (1, 1, "South"),  #(0, -1)
    4 : (0, -1, "West")  #(-1, 0)
}


# Wind direction for our forest
WIND = 2

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

'''

def getColorCell(n):
    if n[0]:
        if n[1]:
            # Burning tree
            return __colors__[3]
        else:
            # Color according to the tree's age
            return __colors__[n[0]]
    else:
        # Empty cell
        return __colors__[0]
    

class Grid:
    _grid = None
    _gridbis = None
    _indexVoisins = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    
    def __init__(self, empty=True):
        
        print("Creating grid of dimensions " + str(__gridDim__))
        
        if empty:
            self._grid = np.zeros(__gridDim__, dtype='int8')
            self._gridbis = np.zeros(__gridDim__, dtype='int8')
        else:
            size = __gridDim__[0] * __gridDim__[1]
            self._grid = np.ones(size, dtype='int8')
            self._grid[:int((1-tree_ratio)*size)] = 0
            np.random.shuffle(self._grid)
            self._gridbis = np.reshape(self._grid, (__gridDim__[0], __gridDim__[1]))
            self._grid = np.reshape(self._grid, (__gridDim__[0], __gridDim__[1]))
        
        assert (np.array_equal(self._grid, self._gridbis))
        nx, ny = __gridDim__

    def indiceVoisins(self, x,y):
        return [(dx+x,dy+y) for (dx,dy) in self._indexVoisins if dx+x >=0 and dx+x < __gridDim__[0] and dy+y>=0 and dy+y < __gridDim__[1]] 

    def voisins(self,x,y):
        return [self._gridbis[vx,vy] for (vx,vy) in self.indiceVoisins(x,y)]
   
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
    

class Forest:

    _trees = None
    _burning = None
    _empties = None
    _old = None
    _young = None
    _burnt = None
    
    def __init__(self, gridTrees, gridBurning, wind=None):
        
        # Grids needed to store burning and tree states of cells
        self._trees = gridTrees
        self._burning = gridBurning
        
        # Counts 
        self._burnt = 0
        self._old = 0
        self._young = __gridDim__[0] * __gridDim__[1] * tree_ratio
        self._empties = __gridDim__[0] * __gridDim__[1] * (1-tree_ratio)
        
        if wind is not None:
            v = winds[wind]
            self._burning._indexVoisins = [ w for w in self._burning._indexVoisins if w[v[0]] != v[1]]
            print(self._burning._indexVoisins)
        
    # Get state of a tree i.e (tree?, burning?)
    def getTree(self, x, y):
        return (self._trees._gridbis[x, y], self._burning._gridbis[x, y])
        
    # Tree igniting treatment
    def ignite_grow(self, x, y):
        neighbours = self._burning.voisins(x, y)

        # Case at least one neighbour is burning
        if 1 in neighbours:
            self._burning[x, y] = 1
            self._burnt += 1

        # Ignite due to lightning
        else:           
            rnd_ignite = random.random()
            if rnd_ignite <= lightning: 
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
        if rnd_growth <= new_growth: 
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
        
        for x in range(__gridDim__[0]):
            for y in range(__gridDim__[1]):
                
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
                    
                    
class Scene:
    _mouseCoords = (0,0)
    _forest = None
    _font = None

    def __init__(self):
        pygame.init()
        self._screen = pygame.display.set_mode(__screenSize__)
        self._font = pygame.font.SysFont('Arial',20)
        self._forest = Forest(Grid(empty=False), Grid(), WIND)

    def drawMe(self):
        if self._forest._trees is None or self._forest._burning is None:
            return
        self._screen.fill((255,255,255))
        for x in range(__gridDim__[0]):
            for y in range(__gridDim__[1]):
                pygame.draw.rect(self._screen, 
                        getColorCell(self._forest.getTree(x,y)),
                        (x*__cellSize__ + 1, y*__cellSize__ + 1, __cellSize__-2, __cellSize__-2))
        
        # Legend
        
        total = __gridDim__[0] * __gridDim__[1] 
        
        pygame.draw.line(self._screen, (0, 0, 0), (900, 0), (900, 1200), width=2)
        
        pygame.draw.rect(self._screen, (0, 0, 0), (915, 15, 30, 30))
        pygame.draw.rect(self._screen, __colors__[2], (920, 20, 20, 20))
        self.drawText("Old tree (" + str(int(self._forest._old)) + " / " + str(np.round(1.*self._forest._old/total * 100, 2)) + "%)", (960, 20))
        
        pygame.draw.rect(self._screen, (0, 0, 0), (915, 55, 30, 30))
        pygame.draw.rect(self._screen, __colors__[1], (920, 60, 20, 20))
        self.drawText("Young tree (" + str(int(self._forest._young)) + " / " + str(np.round(1.*self._forest._young/total * 100, 2)) + "%)", (960, 60))
        
        pygame.draw.rect(self._screen, (0, 0, 0), (915, 95, 30, 30))
        pygame.draw.rect(self._screen, __colors__[3], (920, 100, 20, 20))
        self.drawText("Burning tree (" + str(int(self._forest._burnt)) + " / " + str(np.round(1.*self._forest._burnt/total * 100, 2)) + "%)", (960, 100))
        
        pygame.draw.rect(self._screen, (0, 0, 0), (915, 135, 30, 30))
        pygame.draw.rect(self._screen, __colors__[0], (920, 140, 20, 20))
        self.drawText("Empty cell (" + str(int(self._forest._empties)) + " / " + str(np.round(1.*self._forest._empties/total * 100, 2)) + "%)", (960, 140))
        
        # Parameters
        
        self.drawText("Lightning probability : " + str(lightning*100) + "%", (920, 600))
        self.drawText("Growth probability : " + str(new_growth*100) + "%", (920, 630))
        self.drawText("Initial tree rate : " + str(tree_ratio*100) + "%", (920, 660))
        self.drawText("Wind direction : " + winds[WIND][2], (920, 690))


    def drawText(self, text, position, color = (0,0,0)):
        self._screen.blit(self._font.render(text,1,color),position)

    def update(self):
        self._forest.update()
           
                    
def main():
    scene = Scene()
    done = False
    clock = pygame.time.Clock()
    while done == False:
        scene.drawMe()
        pygame.display.flip()
        scene.update()
        clock.tick(2)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                print("Exiting")
                done=True

    pygame.quit()

if not sys.flags.interactive: main() 
        
        
        
        
        
        
        
        
        
        

