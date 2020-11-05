import pygame as pg

pg.init()
COLOR_INACTIVE = pg.Color((0, 0, 0))
COLOR_ACTIVE = pg.Color((0, 255, 0))
FONT = pg.font.Font(None, 32)


class InputBox:

    def __init__(self, x, y, w, h, screen, text='', min_width=100):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False
        self.screen = screen
        self.min_width = min_width

    def updateText(self, text):
        self.text = text
        self.txt_surface = FONT.render(self.text, True, COLOR_INACTIVE)

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE

        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_RETURN:
                    print(self.text)
                    self.text = ''
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
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
        pg.draw.rect(self.screen, self.color, self.rect, 2)