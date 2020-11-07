import pygame
import pygame.draw
import input_box as ibox
import input_button as ibut
import numpy as np

import forest as ft


# Globals

__clock_tick__ = 2
__screenSize__ = (1250,900)
WATER_COLOR = (50, 50, 255)
COLOR_EMPTY = (255, 255, 255)


# Get the right color for a given cell
def getColorCell(n: tuple) -> tuple:
    if n[2]:
        return WATER_COLOR
    elif n[0]:
        if n[1]:
            # Burning tree, color according to burning time
            orange = 165 - (n[1] * 96 / 9)
            return (255, orange, 0)
        else:
            # Color according to the tree's age
            green = 255 - (n[0] * 155 / 9)
            return (0, green, 0)
    else:
        # Empty cell
        return ft.humidity_color()

class Scene:
    _mouseCoords = (0,0)
    _forest = None
    _font = None

    def __init__(self):
        pygame.init()
        self._screen = pygame.display.set_mode(__screenSize__)
        self._font = pygame.font.SysFont('Arial',20)
        self._forest = ft.Forest()

    # Metho drawing actual forest simulation on the scene 
    def drawMe(self):
        if self._forest._trees is None or self._forest._burning is None:
            return
        self._screen.fill((255,255,255))
        pygame.draw.rect(self._screen, ft.humidity_color(), (0, 0, ft.gr.__gridSize__[0], ft.gr.__gridSize__[1]))

        for x in range(ft.gr.nx):
            for y in range(ft.gr.ny):
                
                color = getColorCell(self._forest.getCell(x,y))
                if color == WATER_COLOR:
                    pygame.draw.rect(self._screen, color, 
                                        (x*ft.gr.__cellSize__, y*ft.gr.__cellSize__, ft.gr.__cellSize__, ft.gr.__cellSize__))
                    '''pygame.draw.rect(self._screen, (0, 130, 255), 
                                        (x*ft.gr.__cellSize__, y*ft.gr.__cellSize__, ft.gr.__cellSize__, ft.gr.__cellSize__), 1)'''
                else:                    
                    pygame.draw.circle(self._screen, color, 
                                        (x*ft.gr.__cellSize__ + 5, y*ft.gr.__cellSize__ + 5), ft.gr.__cellSize__/2)


    def drawText(self, text: str, position: tuple, color = (0,0,0)):
        self._screen.blit(self._font.render(text,1,color),position)

    def drawElement(self, name: str, elem, total: int, x: int, y: int, w: int, h: int, color: tuple):
        pygame.draw.rect(self._screen, color, (x, y, w, h))
        pygame.draw.rect(self._screen, (0, 0, 0), (x, y, w, h), 2)
        self.drawText(name + " (" + str(int(elem)) + " / " + str(np.round(1.*elem/total * 100, 2)) + "%)", (x + 40, y))
    
    def drawLegend(self):
        total = ft.gr.nx * ft.gr.ny 

        # Legend
        pygame.draw.line(self._screen, (0, 0, 0), (900, 0), (900, 1200), width=3)
            
        # Color shades
        for i in range(10):
            # Green shades for trees
            pygame.draw.rect(self._screen, (0, 255 - (i * 155 / 9), 0), (920, 100+2*i, 20, 2))
            # Orange shades for fires
            pygame.draw.rect(self._screen, (255, 165 - (i * 96 / 9), 0), (920, 140+2*i, 20, 2))

        # Black borders
        pygame.draw.rect(self._screen, (0, 0, 0), (920, 100, 20, 20), 2)
        pygame.draw.rect(self._screen, (0, 0, 0), (920, 140, 20, 20), 2)
        
        # Text en measures
        self.drawText("Trees (" + str(int(self._forest._tree)) + " / " + str(np.round(1.*self._forest._tree/total * 100, 2)) + "%)", (960, 100))
        self.drawText("Burning trees (" + str(int(self._forest._burnt)) + " / " + str(np.round(1.*self._forest._burnt/total * 100, 2)) + "%)", (960, 140))
        
        # Legend for empty cells
        self.drawElement("Empty cell", self._forest._empties, total, 920, 180, 20, 20, ft.humidity_color())
        pygame.draw.rect(self._screen, (50, 50, 255), (920, 220, 20, 20))
        pygame.draw.rect(self._screen, (0, 0, 0), (920, 220, 20, 20), 2)
        self.drawText("Water", (960, 220))
        
        # Parameters
        self.drawText("Initial tree rate: " + str(ft.TREE_RATIO*100) + "%", (920, 400))

        pygame.draw.rect(self._screen, ft.humidity_color(), (920, 440, 20, 20))
        pygame.draw.rect(self._screen, (0, 0, 0), (920, 440, 20, 20), 2)
        self.drawText("Humidity rate (%): ", (950, 440))
        self.drawText("Lightning probability (%): ", (920, 500))
        self.drawText("Growth probability (%):", (920, 560))
        self.drawText("Wind direction: ", (920, 645))
        self.drawText("Wind strength [0-" + str(ft.WIND_MAX) + "]:" , (920, 722))
        
    def update(self):
        self._forest.update()



# Updates the wind according to the UI  
def update_wind_dir(buttons: dict, inputs: dict):
    
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
def update_wind_strength(ws_buttons: dict, ws_box, wind_buttons: dict):

    if ft.WIND != 0:

        for key in ws_buttons.keys():

            if ws_buttons[key].active:
                if key == "minus" and ft.WIND_STRENGTH > 0:
                    ft.WIND_STRENGTH -= 1
                    if ft.WIND_STRENGTH == 0:
                        wind_buttons["none"].activate(wind_buttons)
                elif key == "plus" and ft.WIND_STRENGTH < ft.WIND_MAX:
                    ft.WIND_STRENGTH += 1

                ws_box.updateText(str(ft.WIND_STRENGTH))

        

if __name__ == '__main__':

    scene = Scene()
    done = False
    clock = pygame.time.Clock()

    # input boxes for parameters
    input_boxes = {}
    input_boxes["humidity"] = ibox.InputBox(920, 465, 100, 30, scene._screen, 100, 0.0, float, text=str(ft.HUMIDITY * 100))
    input_boxes["lightning"] = ibox.InputBox(920, 525, 100, 30, scene._screen, 100, 0.0, float, text=str(ft.LIGHTNING * 100))
    input_boxes["new_growth"] = ibox.InputBox(920, 585, 100, 30, scene._screen, 100, 0.0, float, text=str(ft.NEW_GROWTH * 100))
    input_boxes["wind_strength"] = ibox.InputBox(1110, 720, 25, 30, scene._screen, ft.WIND_MAX, 0, int, text=str(ft.WIND_STRENGTH), min_width=25, writeable=False)

    # buttons for wind direction
    wind_buttons = {}
    wind_buttons["none"] = ibut.InputButton(1120, 650, 15, 15, scene._screen, active=True)
    wind_buttons["north"] = ibut.InputButton(1100, 620, 55, 25, scene._screen, text=str(ft.WINDS[1][2]))
    wind_buttons["east"] = ibut.InputButton(1155, 645, 55, 25, scene._screen, text=str(ft.WINDS[2][2]))
    wind_buttons["south"] = ibut.InputButton(1100, 670, 55, 25, scene._screen, text=str(ft.WINDS[3][2]))
    wind_buttons["west"] = ibut.InputButton(1045, 645, 55, 25, scene._screen, text=str(ft.WINDS[4][2]))

    # buttons for wind strength
    ws_buttons = {}
    ws_buttons["minus"] = ibut.InputButton(1080, 725, 20, 20, scene._screen, text="-", blink=True)
    ws_buttons["plus"] = ibut.InputButton(1145, 725, 20, 20, scene._screen, text="+", blink=True)

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
        ft.HUMIDITY = input_boxes["humidity"].try_except_cast() / 100
        ft.LIGHTNING = input_boxes["lightning"].try_except_cast() / 100
        ft.NEW_GROWTH = input_boxes["new_growth"].try_except_cast() / 100
        ft.WIND_STRENGTH = input_boxes["wind_strength"].try_except_cast()
       
        # Check which wind button is active and update the wind parameters accordingly     
        update_wind_dir(wind_buttons, input_boxes)
        update_wind_strength(ws_buttons, input_boxes["wind_strength"], wind_buttons)

    pygame.quit()
        