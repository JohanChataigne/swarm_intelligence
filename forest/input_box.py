import pygame as pg
import numpy as np

pg.init()
COLOR_INACTIVE = pg.Color((0, 0, 0))
COLOR_ACTIVE = pg.Color((0, 255, 0))
FONT = pg.font.Font(None, 32)


class InputBox:

    def __init__(self, x: int, y: int, w: int, h: int, screen, value: float, max_val: float, except_val: float, cast: type, min_width=100, writeable=True, increment=0, decimals=1):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = str(value)
        self.txt_surface = FONT.render(self.text, True, self.color)
        self.active = False
        self.screen = screen
        self.value = value
        self.max_val = max_val
        self.except_val = except_val
        self.cast = cast
        self.increment = increment
        self.min_width = min_width
        self.writeable = writeable
        self.increment = increment
        self.init_increment = increment
        self.nb_increment = 1
        self.decimals = decimals

    def updateText(self, val: float):
        self.text = str(round(val, self.decimals))
        self.txt_surface = FONT.render(self.text, True, COLOR_INACTIVE)

    # Try to cast 'try_val' with cast() and assign it to var, or 'except_val' if it fails
    def try_except_cast(self):
        try:
            self.value = self.cast(self.text)
            if self.value > self.max_val:
                self.value = self.max_val
                self.updateText(self.value)

        except ValueError:
            self.value = self.except_val
        
        return self.value

    def handle_event(self, event):
        if self.writeable:
            if event.type == pg.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect.
                if self.rect.collidepoint(event.pos):
                    # Toggle the active variable.
                    self.active = not self.active
                else:
                    self.active = False
                # Change the current color of the input box.
                self.updateText(self.try_except_cast())

            elif event.type == pg.KEYDOWN and self.active:
                key = event.key

                if key == pg.K_RETURN:
                    self.active = False
                    self.text = str(self.try_except_cast())

                elif key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]

                elif key == pg.K_PERIOD or key == pg.K_SEMICOLON:
                    self.text += '.'

                elif key == pg.K_RIGHT or key == pg.K_UP:
                    if self.nb_increment < 0:
                        self.nb_increment = 0
                        self.increment = self.init_increment

                    self.value += self.increment
                    if self.value > self.max_val:
                        self.value = self.max_val

                    self.nb_increment += 1
                    if self.nb_increment == 4:
                        self.nb_increment = 1
                        self.increment *= 2
                    self.updateText(self.value)

                elif key == pg.K_LEFT or key == pg.K_DOWN:
                    if self.nb_increment > 0:
                        self.nb_increment = 0
                        self.increment = self.init_increment

                    self.value -= self.increment
                    if self.value < 0:
                        self.value = 0

                    self.nb_increment -= 1
                    if self.nb_increment == -4:
                        self.nb_increment = -1
                        self.increment *= 2
                    self.updateText(self.value)
                    
                elif event.unicode.isdigit():
                    self.text += event.unicode

                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, COLOR_INACTIVE)
                
    def update(self):
        # Resize the box if the text is too long.
        # width = max(200, )
        self.rect.w = max(self.min_width, self.txt_surface.get_width()+10)

    def draw(self):
        # Blit the text.
        self.screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        pg.draw.rect(self.screen, self.color, self.rect, 2)