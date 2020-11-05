import pygame
import pygame.draw
import input_box as ibox
import input_button as ibut
import numpy as np

import forest as ft


# Globals
__clock_tick__ = 2
__colors__ = [(255,255,255),(0,255,0),(0, 86, 27),(255,140,0)]
__screenSize__ = (1250,900)


# Get the right color for a given cell
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


class Scene:
    _mouseCoords = (0,0)
    _forest = None
    _font = None

    def __init__(self):
        pygame.init()
        self._screen = pygame.display.set_mode(__screenSize__)
        self._font = pygame.font.SysFont('Arial',20)
        self._forest = ft.Forest(ft.gr.Grid(empty=False, ratio=ft.TREE_RATIO), ft.gr.Grid())

    # Metho drawing actual forest simulation on the scene 
    def drawMe(self):
        if self._forest._trees is None or self._forest._burning is None:
            return
        self._screen.fill((255,255,255))
        for x in range(ft.gr.nx):
            for y in range(ft.gr.ny):
                pygame.draw.rect(self._screen, 
                        getColorCell(self._forest.getTree(x,y)),
                        (x*ft.gr.__cellSize__ + 1, y*ft.gr.__cellSize__ + 1, ft.gr.__cellSize__-2, ft.gr.__cellSize__-2))


    def drawText(self, text, position, color = (0,0,0)):
        self._screen.blit(self._font.render(text,1,color),position)
    
    def drawLegend(self):
        total = ft.gr.nx * ft.gr.ny 

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
        self.drawText("Initial tree rate: " + str(ft.TREE_RATIO*100) + "%", (920, 460))
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
    
    # List of the states of each wind button
    states = [button.active for button in buttons.values()]
    
    # Check which button is active and update win accordingly
    for index, state in enumerate(states):
        
        if state:
            ft.WIND = index
            if index != 0:
                if ft.WIND_STRENGTH == 0:
                    ft.WIND_STRENGTH = 1
            else:
                ft.WIND_STRENGTH = 0

            inputs["wind_strength"].updateText(str(ft.WIND_STRENGTH))
            return
        
        
if __name__ == '__main__':

    scene = Scene()
    done = False
    clock = pygame.time.Clock()

    # input boxes for parameters
    input_boxes = {}
    input_boxes["lightning"] = ibox.InputBox(920, 525, 40, 30, scene._screen, text=str(ft.LIGHTNING * 100))
    input_boxes["new_growth"] = ibox.InputBox(920, 585, 40, 30, scene._screen, text=str(ft.NEW_GROWTH * 100))
    input_boxes["wind_strength"] = ibox.InputBox(920, 705, 40, 30, scene._screen, text=str(ft.WIND_STRENGTH))

    # buttons for wind direction
    wind_buttons = {}
    wind_buttons["none"] = ibut.InputButton(1120, 650, 15, 15, scene._screen, active=True)
    wind_buttons["north"] = ibut.InputButton(1100, 620, 55, 25, scene._screen, text=str(ft.WINDS[1][2]))
    wind_buttons["east"] = ibut.InputButton(1155, 645, 55, 25, scene._screen, text=str(ft.WINDS[2][2]))
    wind_buttons["south"] = ibut.InputButton(1100, 670, 55, 25, scene._screen, text=str(ft.WINDS[3][2]))
    wind_buttons["west"] = ibut.InputButton(1045, 645, 55, 25, scene._screen, text=str(ft.WINDS[4][2]))

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
        ft.LIGHTNING = try_except_cast(input_boxes["lightning"].text, 0, float) / 100
        ft.NEW_GROWTH = try_except_cast(input_boxes["new_growth"].text, 0, float) / 100
        ft.WIND_STRENGTH = try_except_cast(input_boxes["wind_strength"].text, -1, int)
       
        # Check which wind button is active and update the wind parameters accordingly     
        update_wind(wind_buttons, input_boxes)

    pygame.quit()
        