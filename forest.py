import sys, math, random
import pygame
import pygame.draw
import numpy as np
import input_box as ibox
import input_button as ibut

__screenSize__ = (1250,900)
__gridSize__ = (900,900) 
__cellSize__ = 10 
__gridDim__ = tuple(map(lambda x: int(x/__cellSize__), __gridSize__))
nx, ny = __gridDim__
__clock_tick__ = 2

__colors__ = [(255,255,255),(0,255,0),(0, 86, 27),(255,140,0)]

lightning = 0.0000 #Probability of lightning
new_growth = 0.002 #Probability of new growth
tree_ratio = 0.50 #Tree rate in the space
river = true
lakes = 0


# Map winds with their opposite direction (sense, direction, label)
winds = {
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
        
        if empty:
            self._grid = np.zeros(__gridDim__, dtype='int8')
            self._gridbis = np.zeros(__gridDim__, dtype='int8')
        else:
            size = nx * ny
            self._grid = np.ones(size, dtype='int8')
            self._grid[:int((1-tree_ratio)*size)] = 0
            np.random.shuffle(self._grid)
            self._gridbis = np.reshape(self._grid, (nx, ny))
            self._grid = np.reshape(self._grid, (nx, ny))
        
        assert (np.array_equal(self._grid, self._gridbis))

    def resetIndexVoisins(self):
        self._indexVoisins = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

    def indiceVoisins(self, x,y):
        return [(dx+x,dy+y) for (dx,dy) in self._indexVoisins if dx+x >=0 and dx+x < nx and dy+y>=0 and dy+y < ny] 

    def voisins(self,x,y):
        return [self._gridbis[vx,vy] for (vx,vy) in self.indiceVoisins(x,y)]
    
    def furtherNeighbours(self, x, y, d):
        neighbours = self.indiceVoisins(x, y)
        further_neighbours = neighbours.copy()
        
        # We dont want to exceed a certain wind strength
        if d > 3: 
            d = 3
        
        for k in range(d-1):
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
        self._young = nx * ny * tree_ratio
        self._init = self._young
        self._empties = nx * ny * (1-tree_ratio)

        # If no lightning probability, one tree ignites at the beginning (usefull for percolation)
        if lightning == 0:
            bx = random.randint(0, nx - 1)
            by = random.randint(0, ny - 1)
            while self._trees[bx, by] == 0:
                bx = random.randint(0, nx - 1)
                by = random.randint(0, ny - 1)
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
            v = winds[WIND]
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
        
        for x in range(nx):
            for y in range(ny):
                
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
        self._forest = Forest(Grid(empty=False), Grid())

    # Metho drawing actual forest simulation on the scene 
    def drawMe(self):
        if self._forest._trees is None or self._forest._burning is None:
            return
        self._screen.fill((255,255,255))
        for x in range(nx):
            for y in range(ny):
                pygame.draw.rect(self._screen, 
                        getColorCell(self._forest.getTree(x,y)),
                        (x*__cellSize__ + 1, y*__cellSize__ + 1, __cellSize__-2, __cellSize__-2))


    def drawText(self, text, position, color = (0,0,0)):
        self._screen.blit(self._font.render(text,1,color),position)
    
    def drawLegend(self):
        total = nx * ny 

        # Legend
        pygame.draw.line(self._screen, (0, 0, 0), (900, 0), (900, 1200), width=2)
        
        pygame.draw.rect(self._screen, (0, 0, 0), (915, 95, 30, 30))
        pygame.draw.rect(self._screen, __colors__[2], (920, 100, 20, 20))
        self.drawText("Old tree (" + str(int(self._forest._old)) + " / " + str(np.round(1.*self._forest._old/total * 100, 2)) + "%)", (960, 100))
        
        pygame.draw.rect(self._screen, (0, 0, 0), (915, 135, 30, 30))
        pygame.draw.rect(self._screen, __colors__[1], (920, 140, 20, 20))
        self.drawText("Young tree (" + str(int(self._forest._young)) + " / " + str(np.round(1.*self._forest._young/total * 100, 2)) + "%)", (960, 140))
        
        pygame.draw.rect(self._screen, (0, 0, 0), (915, 175, 30, 30))
        pygame.draw.rect(self._screen, __colors__[3], (920, 180, 20, 20))
        self.drawText("Burning tree (" + str(int(self._forest._burnt)) + " / " + str(np.round(1.*self._forest._burnt/total * 100, 2)) + "%)", (960, 180))
        
        pygame.draw.rect(self._screen, (0, 0, 0), (915, 215, 30, 30))
        pygame.draw.rect(self._screen, __colors__[0], (920, 220, 20, 20))
        self.drawText("Empty cell (" + str(int(self._forest._empties)) + " / " + str(np.round(1.*self._forest._empties/total * 100, 2)) + "%)", (960, 220))
        
        # Parameters
        self.drawText("Initial tree rate: " + str(tree_ratio*100) + "%", (920, 460))
        self.drawText("Lightning probability (%): ", (920, 500))
        self.drawText("Growth probability (%):", (920, 560))
        self.drawText("Wind direction: ", (920, 645))
        self.drawText("Wind strength: ", (920, 680))
        
    def update(self):
        self._forest.update()


# Try to cast 'try_val' with cast() and assign it to var, or 'except_val' if it fails
def try_except_cast(try_val, except_val, cast):
    try:
        ret = cast(try_val)
    except ValueError:
        ret = except_val
    
    return ret
        
# Updates the wind according to the UI  
def update_wind(buttons, inputs):
    global WIND
    global WIND_STRENGTH
    
    # List of the states of each wind button
    states = [button.active for button in buttons.values()]
    
    # Check which button is active and update win accordingly
    for index, state in enumerate(states):
        
        if state:
            WIND = index
            if index != 0:
                if WIND_STRENGTH == 0:
                    WIND_STRENGTH = 1
            else:
                WIND_STRENGTH = 0

            inputs["wind_strength"].updateText(str(WIND_STRENGTH))
            return


if __name__ == '__main__':

    scene = Scene()
    done = False
    clock = pygame.time.Clock()

    # input boxes for parameters
    input_boxes = {}
    input_boxes["lightning"] = ibox.InputBox(920, 525, 40, 30, scene._screen, text=str(lightning * 100))
    input_boxes["new_growth"] = ibox.InputBox(920, 585, 40, 30, scene._screen, text=str(new_growth * 100))
    input_boxes["wind_strength"] = ibox.InputBox(920, 705, 40, 30, scene._screen, text=str(WIND_STRENGTH))

    # buttons for wind direction
    wind_buttons = {}
    wind_buttons["none"] = ibut.InputButton(1120, 650, 15, 15, scene._screen, active=True)
    wind_buttons["north"] = ibut.InputButton(1100, 620, 55, 25, scene._screen, text=str(winds[1][2]))
    wind_buttons["east"] = ibut.InputButton(1155, 645, 55, 25, scene._screen, text=str(winds[2][2]))
    wind_buttons["south"] = ibut.InputButton(1100, 670, 55, 25, scene._screen, text=str(winds[3][2]))
    wind_buttons["west"] = ibut.InputButton(1045, 645, 55, 25, scene._screen, text=str(winds[4][2]))

    # Main loop
    while done == False:

        # Display the screen
        scene.drawMe()
        scene.drawLegend()
        for box in input_boxes.values():
            box.draw()
        for but in wind_buttons.values():
            but.draw()
        pygame.display.flip()

        # Update the state of the forest
        scene.update()

        clock.tick(__clock_tick__)
        events = pygame.event.get()

        # Handle the events
        for event in events:
            if event.type == pygame.QUIT: 
                print("Exiting")
                done=True

            for box in input_boxes.values():
                box.handle_event(event)

            for but in wind_buttons.values():
                but.handle_event(event, wind_buttons)

        
        for box in input_boxes.values():
           box.update()
        
        # Convert input we get from the UI
        lightning = try_except_cast(input_boxes["lightning"].text, 0, float) / 100
        new_growth = try_except_cast(input_boxes["new_growth"].text, 0, float) / 100
        WIND_STRENGTH = try_except_cast(input_boxes["wind_strength"].text, -1, int)
       
        # Check which wind button is active and update the wind parameters accordingly     
        update_wind(wind_buttons, input_boxes)

    pygame.quit()
        
        
        
        
        
        
        
        
        
        

