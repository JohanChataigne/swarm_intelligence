import sys, math, random
import pygame
import pygame.draw
import numpy as np

__screenSize__ = (900,900) #(1280,1280)
__cellSize__ = 10 
__gridDim__ = tuple(map(lambda x: int(x/__cellSize__), __screenSize__))
__density__ = 3 

__colors__ = [(255,255,255),(0,255,0),(255,0,0)]


glidergun=[
  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0],
  [0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
  [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
  [1,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
  [1,1,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1,1,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0],
  [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
  [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
  [0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]

def getColorCell(n):
    return __colors__[n]

class Grid:
    _grid= None
    _gridbis = None
    _indexVoisins = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    
    def __init__(self):
        
        print("Creating a grid of dimen255,140,0sions " + str(__gridDim__))
        self._grid = np.zeros(__gridDim__, dtype='int8')
        self._gridbis = np.zeros(__gridDim__, dtype='int8')
        nx, ny = __gridDim__
        
        if False: # True to init with one block at the center
            self._grid[nx//2,ny//2] = 1
            self._grid[nx//2+1,ny//2] = 1
            self._grid[nx//2,ny//2+1] = 1
            self._grid[nx//2+1,ny//2+1] = 1
            
        elif False: # True to init with random values at the center
            mx, my = 20, 16
            ones = np.random.random((mx, my)) > 0.75
            self._grid[nx//2-mx//2:nx//2+mx//2, ny//2-my//2:ny//2+my//2] = ones
            
        else: # Else if init with glider gun

            a = np.fliplr(np.rot90(np.array(glidergun),3))
            mx, my = a.shape
            self._grid[nx//2-mx//2:nx//2+mx//2, ny//2-my//2:ny//2+my//2] = a



    def indiceVoisins(self, x,y):
        return [(dx+x,dy+y) for (dx,dy) in self._indexVoisins if dx+x >=0 and dx+x < __gridDim__[0] and dy+y>=0 and dy+y < __gridDim__[1]] 

    def voisins(self,x,y):
        return [self._grid[vx,vy] for (vx,vy) in self.indiceVoisins(x,y)]
   
    def sommeVoisins(self, x, y):
        return sum(self.voisins(x,y))

    def sumEnumerate(self):
        return [(c, self.sommeVoisins(c[0], c[1])) for c, _ in np.ndenumerate(self._grid)]

    def drawMe(self):
        pass

class Scene:
    _mouseCoords = (0,0)
    _grid = None
    _font = None

    def __init__(self):
        pygame.init()
        self._screen = pygame.display.set_mode(__screenSize__)
        self._font = pygame.font.SysFont('Arial',25)
        self._grid = Grid()

    def drawMe(self):
        if self._grid._grid is None:
            return
        self._screen.fill((255,255,255))
        for x in range(__gridDim__[0]):
            for y in range(__gridDim__[1]):
                pygame.draw.rect(self._screen, 
                        getColorCell(self._grid._grid.item((x,y))),
                        (x*__cellSize__ + 1, y*__cellSize__ + 1, __cellSize__-2, __cellSize__-2))


    def drawText(self, text, position, color = (255,64,64)):
        self._screen.blit(self._font.render(text,1,color),position)

    def update(self):
        '''B234/S rule'''
        for c, s in self._grid.sumEnumerate():
            self._grid._gridbis[c[0], c[1]] = 1 if (2 <= s <= 4) and self._grid._grid[c[0],c[1]] == 0 else 0 
        self._grid._grid = np.copy(self._grid._gridbis)

    def updatebis(self):
        for c, s in self._grid.sumEnumerate():
            if self._grid._grid[c[0],c[1]] == 1:
                ret = 2 <= s <= 3 
            else:
                ret = s == 3
            self._grid._gridbis[c[0], c[1]] = 1 if ret else 0
        self._grid._grid = np.copy(self._grid._gridbis)

    def updateBrain(self):
        for c, s in self._grid.sumEnumerate():
            if self._grid._grid[c[0],c[1]] == 2:
                ret = 0
            elif self._grid._grid[c[0],c[1]] == 1:
                ret = 2
            else:
                ret = 1 if s == 2 else 0
            self._grid._gridbis[c[0], c[1]] = ret
        self._grid._grid = np.copy(self._grid._gridbis)

    def updateRule(self, B, S):
        # Maze is B3/S12345
        ''' Many rules in https://www.conwaylife.com/wiki/List_of_Life-like_cellular_automata '''
        for c, s in self._grid.sumEnumerate():
            if self._grid._grid[c[0],c[1]] == 1:
                ret = s in S
            else:
                ret = s in B
            self._grid._gridbis[c[0], c[1]] = 1 if ret else 0
        self._grid._grid = np.copy(self._grid._gridbis)


    def eventClic(self, coord, b):
        pass

    def recordMouseMove(self, coord):
        pass

def main():
    scene = Scene()
    done = False
    clock = pygame.time.Clock()
    while done == False:
        scene.drawMe()
        pygame.display.flip()
        #scene.updatebis()
        scene.updateBrain()
        #scene.updateRule([3],[2,3])
        #scene.updateRule([2,3,4],[])
        #scene.updateRule([3],[1,2,3,4,5])
        clock.tick(2)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                print("Exiting")
                done=True

    pygame.quit()

if not sys.flags.interactive: main()

