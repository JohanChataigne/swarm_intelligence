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

    def drawElement(self, name, elem, total, x, y, w, h, color):
        pygame.draw.rect(self._screen, color, (x, y, w, h))
        pygame.draw.rect(self._screen, (0, 0, 0), (x, y, w, h), 3)
        self.drawText(name + " (" + str(int(elem)) + " / " + str(np.round(1.*elem/total * 100, 2)) + "%)", (x + 40, y))
    
    def drawLegend(self):
        total = ft.gr.nx * ft.gr.ny 

        # Legend
        pygame.draw.line(self._screen, (0, 0, 0), (900, 0), (900, 1200), width=2)
        
        self.drawElement("Old tree", self._forest._old, total, 920, 100, 20, 20, __colors__[2])
        self.drawElement("Young tree", self._forest._young, total, 920, 140, 20, 20, __colors__[1])
        self.drawElement("Burning tree", self._forest._burnt, total, 920, 180, 20, 20, __colors__[3])
        self.drawElement("Empty cell", self._forest._empties, total, 920, 220, 20, 20, __colors__[0])
        
        # Parameters
        self.drawText("Initial tree rate: " + str(ft.TREE_RATIO*100) + "%", (920, 460))
        self.drawText("Lightning probability (%): ", (920, 500))
        self.drawText("Growth probability (%):", (920, 560))
        self.drawText("Wind direction: ", (920, 645))
        self.drawText("Wind strength: ", (920, 720))
        
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
def update_wind_dir(buttons, inputs):
    
    # List of the states of each wind button
    states = [button.active for button in buttons.values()]
    
    # Check which button is active and update wind accordingly
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

# Updates the wind according to the UI  
def update_wind_strength(ws_buttons, ws_box):

    if ft.WIND != 0:

        for key in ws_buttons.keys():

            if ws_buttons[key].active:
                if key == "minus" and ft.WIND_STRENGTH > 1:
                    ft.WIND_STRENGTH -= 1
                elif key == "plus" and ft.WIND_STRENGTH < 3:
                    ft.WIND_STRENGTH += 1

                ws_box.updateText(str(ft.WIND_STRENGTH))
        

if __name__ == '__main__':

    scene = Scene()
    done = False
    clock = pygame.time.Clock()

    # input boxes for parameters
    input_boxes = {}
    input_boxes["lightning"] = ibox.InputBox(920, 525, 40, 30, scene._screen, text=str(ft.LIGHTNING * 100))
    input_boxes["new_growth"] = ibox.InputBox(920, 585, 40, 30, scene._screen, text=str(ft.NEW_GROWTH * 100))
    input_boxes["wind_strength"] = ibox.InputBox(1080, 720, 25, 30, scene._screen, text=str(ft.WIND_STRENGTH), min_width=25, writeable=False)

    # buttons for wind direction
    wind_buttons = {}
    wind_buttons["none"] = ibut.InputButton(1120, 650, 15, 15, scene._screen, active=True)
    wind_buttons["north"] = ibut.InputButton(1100, 620, 55, 25, scene._screen, text=str(ft.WINDS[1][2]))
    wind_buttons["east"] = ibut.InputButton(1155, 645, 55, 25, scene._screen, text=str(ft.WINDS[2][2]))
    wind_buttons["south"] = ibut.InputButton(1100, 670, 55, 25, scene._screen, text=str(ft.WINDS[3][2]))
    wind_buttons["west"] = ibut.InputButton(1045, 645, 55, 25, scene._screen, text=str(ft.WINDS[4][2]))

    # buttons for wind strength
    ws_buttons = {}
    ws_buttons["minus"] = ibut.InputButton(1050, 725, 20, 20, scene._screen, text="-", blink=True)
    ws_buttons["plus"] = ibut.InputButton(1115, 725, 20, 20, scene._screen, text="+", blink=True)

    # Main loop
    while done == False:

        # Display the screen
        scene.drawMe()
        scene.drawLegend()
        for box in input_boxes.values():
            box.draw()
        for but in wind_buttons.values():
            but.draw()
        for but in ws_buttons.values():
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
            for but in ws_buttons.values():
                but.handle_event(event, ws_buttons)

        
        for box in input_boxes.values():
           box.update()
        
        # Convert input we get from the UI
        ft.LIGHTNING = try_except_cast(input_boxes["lightning"].text, 0, float) / 100
        ft.NEW_GROWTH = try_except_cast(input_boxes["new_growth"].text, 0, float) / 100
        ft.WIND_STRENGTH = try_except_cast(input_boxes["wind_strength"].text, -1, int)
       
        # Check which wind button is active and update the wind parameters accordingly     
        update_wind_dir(wind_buttons, input_boxes)
        update_wind_strength(ws_buttons, input_boxes["wind_strength"])

    pygame.quit()
        