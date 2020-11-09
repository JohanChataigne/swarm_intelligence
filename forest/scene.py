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
def getColorCell(cell: tuple) -> tuple:
    # The cell contains water
    if cell[2]:
        return WATER_COLOR
    
    # The cell contains a tree
    elif cell[0]:

        # The cell contains a burning tree
        if cell[1]:
            # Burning tree, color according to burning time
            orange = 165 - (cell[1] * 120 / 9)
            return (255, orange, 0)
        else:
            # Color according to the tree's age
            green = 255 - (cell[0] * 155 / 9)
            return (0, green, 0)

    # The cell is empty
    else:
        return ft.humidity_color()

class Scene:
    _mouseCoords = (0,0)
    _forest = None
    _font = None
    _input_boxes = {}
    _wind_buttons = {}
    _ws_buttons = {}

    def __init__(self):
        pygame.init()
        self._screen = pygame.display.set_mode(__screenSize__)
        self._font = pygame.font.SysFont('Arial',20)
        self._forest = ft.Forest()

        # input boxes for parameters
        self._input_boxes["humidity"] = ibox.InputBox(920, 465, 100, 30, self._screen, ft.HUMIDITY * 100, 100, 0.0, float, increment=1, decimals=1)
        self._input_boxes["lightning"] = ibox.InputBox(920, 525, 100, 30, self._screen, ft.LIGHTNING * 100, 100, 0.0, float, increment=0.001, decimals=3)
        self._input_boxes["new_growth"] = ibox.InputBox(920, 585, 100, 30, self._screen, ft.NEW_GROWTH * 100, 100, 0.0, float, increment=0.1, decimals=1)
        self._input_boxes["wind_strength"] = ibox.InputBox(1110, 720, 25, 30, self._screen, ft.WIND_STRENGTH, ft.WIND_MAX, 0, int, min_width=25, writeable=False)

        # buttons for wind direction
        self._wind_buttons["none"] = ibut.InputButton(1120, 650, 15, 15, self._screen, active=True)
        self._wind_buttons["north"] = ibut.InputButton(1100, 620, 55, 25, self._screen, text=str(ft.WINDS[1][2]))
        self._wind_buttons["east"] = ibut.InputButton(1155, 645, 55, 25, self._screen, text=str(ft.WINDS[2][2]))
        self._wind_buttons["south"] = ibut.InputButton(1100, 670, 55, 25, self._screen, text=str(ft.WINDS[3][2]))
        self._wind_buttons["west"] = ibut.InputButton(1045, 645, 55, 25, self._screen, text=str(ft.WINDS[4][2]))

        # buttons for wind strength
        self._ws_buttons["minus"] = ibut.InputButton(1080, 725, 20, 20, self._screen, text="-", blink=True)
        self._ws_buttons["plus"] = ibut.InputButton(1145, 725, 20, 20, self._screen, text="+", blink=True)

    def draw_clouds(self):
        if self._forest._clouds is not None:
            for x in range(ft.gr.nx):
                for y in range(ft.gr.ny):
                    if self._forest._clouds[x, y]:
                        color = ft.clouds_color(ft.humidity_color())
                        pygame.draw.circle(self._screen, color, 
                                        (x*ft.gr.__cellSize__  + 5, y*ft.gr.__cellSize__ +5), ft.gr.__cellSize__ *0.7)


    def draw_background(self):
        self._screen.fill((255,255,255))
        pygame.draw.rect(self._screen, ft.humidity_color(), (0, 0, ft.gr.__gridSize__[0], ft.gr.__gridSize__[1]))

    # Metho drawing actual forest simulation on the scene 
    def draw_cells(self):
        if self._forest._trees is None or self._forest._burning is None:
            return
        
        for x in range(ft.gr.nx):
            for y in range(ft.gr.ny):
                
                cell = self._forest.getCell(x,y)
                if cell[2]:
                    color = WATER_COLOR
                    if cell[3]:
                        color = ft.clouds_color(color)
                    pygame.draw.rect(self._screen, color, 
                                        (x*ft.gr.__cellSize__, y*ft.gr.__cellSize__, ft.gr.__cellSize__, ft.gr.__cellSize__))
                elif cell[0]:
                    color = getColorCell(cell)
                    if cell[3]:
                        color = ft.clouds_color(color)                    
                    pygame.draw.circle(self._screen, color, 
                                        (x*ft.gr.__cellSize__ + 5, y*ft.gr.__cellSize__ + 5), ft.gr.__cellSize__/2)


    def draw_text(self, text: str, position: tuple, color=(0,0,0)):
        self._screen.blit(self._font.render(text,1,color),position)

    def draw_element(self, name: str, elem: int, total: int, x: int, y: int, w: int, h: int, color: tuple):
        pygame.draw.rect(self._screen, color, (x, y, w, h))
        pygame.draw.rect(self._screen, (0, 0, 0), (x, y, w, h), 2)
        self.draw_text(name + " (" + str(int(elem)) + " / " + str(np.round(1.*elem/total * 100, 2)) + "% of cells)", (x + 40, y))
    
    def draw_legend(self):
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
        self.draw_text("Trees (" + str(int(self._forest._tree)) + " / " + str(np.round(1.*self._forest._tree/total * 100, 2)) + "% of cells)", (960, 100))
        self.draw_text("Burning trees (" + str(int(self._forest._burnt)) + " / " + str(np.round(1.*self._forest._burnt/self._forest._tree * 100, 2)) + "% of trees)", (960, 140))
        
        # Legend for empty cells
        self.draw_element("Empty cell", self._forest._empties, total, 920, 180, 20, 20, ft.humidity_color())
        pygame.draw.rect(self._screen, (50, 50, 255), (920, 220, 20, 20))
        pygame.draw.rect(self._screen, (0, 0, 0), (920, 220, 20, 20), 2)
        self.draw_text("Water", (960, 220))
        
        # Parameters
        self.draw_text("Initial tree rate: " + str(ft.TREE_RATIO*100) + "%", (920, 400))

        pygame.draw.rect(self._screen, ft.humidity_color(), (920, 440, 20, 20))
        pygame.draw.rect(self._screen, (0, 0, 0), (920, 440, 20, 20), 2)
        self.draw_text("Humidity rate (%): ", (950, 440))
        self.draw_text("Lightning probability (%): ", (920, 500))
        self.draw_text("Growth probability (%):", (920, 560))
        self.draw_text("Wind direction: ", (920, 645))
        self.draw_text("Wind strength [0-" + str(ft.WIND_MAX) + "]:" , (920, 722))

    def draw_boxes_buttons(self):
        for box in self._input_boxes.values():
            box.draw()
        for but in self._wind_buttons.values():
            but.draw()
        for but in self._ws_buttons.values():
            but.draw()

    # Display all the elements of the screen
    def draw(self):
        self.draw_background()
        self.draw_clouds()
        self.draw_cells()
        self.draw_legend()
        self.draw_boxes_buttons()

    def handle_event(self, event):
        # Handle the event for all the input boxes and buttons

        for box in self._input_boxes.values():
            box.handle_event(event)
        for but in self._wind_buttons.values():
            but.handle_event(event, self._wind_buttons)
        for but in self._ws_buttons.values():
            but.handle_event(event, self._ws_buttons)

    # Updates the wind according to the UI  
    def update_wind_dir(self):
    
        # List of the states of each wind button
        states = [button.active for button in self._wind_buttons.values()]
        
        # Check which button is active and update wind accordingly
        for index, state in enumerate(states):
            
            if state:
                ft.WIND = index
                if index != 0:
                    if ft.WIND_STRENGTH == 0:
                        ft.WIND_STRENGTH = 1
                else:
                    ft.WIND_STRENGTH = 0

                self._input_boxes["wind_strength"].updateText(ft.WIND_STRENGTH)
                return

    # Updates the wind strength according to the button clicked
    def update_wind_strength(self):

        if ft.WIND != 0:

            for key in self._ws_buttons.keys():

                if self._ws_buttons[key].active:
                    if key == "minus" and ft.WIND_STRENGTH > 0:
                        ft.WIND_STRENGTH -= 1
                        if ft.WIND_STRENGTH == 0:
                            self._wind_buttons["none"].activate(self._wind_buttons)
                    elif key == "plus" and ft.WIND_STRENGTH < ft.WIND_MAX:
                        ft.WIND_STRENGTH += 1

                    self._input_boxes["wind_strength"].updateText(ft.WIND_STRENGTH)
        
    def update(self):
        # Update the state of the forest
        self._forest.update()

        # Check which wind button is active and update the wind parameters accordingly     
        self.update_wind_dir()
        self.update_wind_strength()

        # Update the position of the clouds
        self._forest.update_clouds()
        

if __name__ == '__main__':

    scene = Scene()
    done = False
    clock = pygame.time.Clock()

    # Main loop
    while done == False:

        # Draw the elements of the screen
        scene.draw()
        # Display the entire screen
        pygame.display.flip()
    
        clock.tick(__clock_tick__)

        # Handle all the events happening (clicks, key pressed)
        events = pygame.event.get()
        for event in events:

            # Exit the game
            if event.type == pygame.QUIT: 
                print("Exiting")
                done=True

            scene.handle_event(event)
        
        # Update the size of the input boxes
        for box in scene._input_boxes.values():
           box.update()

        
        # Update the forest global variables from the content of the input boxes
        ft.HUMIDITY = scene._input_boxes["humidity"].try_except_cast() / 100
        ft.LIGHTNING = scene._input_boxes["lightning"].try_except_cast() / 100
        ft.NEW_GROWTH = scene._input_boxes["new_growth"].try_except_cast() / 100
        ft.WIND_STRENGTH = scene._input_boxes["wind_strength"].try_except_cast()
       
       # Update the state of the forest
        scene.update()


    pygame.quit()
        