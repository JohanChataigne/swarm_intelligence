import pygame as pg

pg.init()
COLOR_INACTIVE = pg.Color((180, 180, 180))
COLOR_ACTIVE = pg.Color((100, 100, 100))
COLOR_TEXT = pg.Color((0, 0, 0))
FONT = pg.font.Font(None, 25)


class InputButton:

    def __init__(self, x: int, y: int, w: int, h: int, screen, text='', active=False, blink=False):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.screen = screen
        self.text = text
        self.active = active
        self.blink = blink
        self.txt_surface = FONT.render(text, True, COLOR_TEXT)

    def activate(self, buttons):

        self.active = True
        self.color = COLOR_ACTIVE
        
        if buttons is not None:
            for but in [b for b in buttons.values() if b != self]:
                but.active = False
                but.color = COLOR_INACTIVE

    def handle_event(self, event, buttons=None):
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.activate(buttons)

    def update(self):
        # Resize the box if the text is too long.
        self.rect.w = self.txt_surface.get_width()+10

    def draw_button(self):

        # Blit the rect.
        pg.draw.rect(self.screen, self.color, self.rect)
        pg.draw.rect(self.screen, COLOR_TEXT, self.rect, 1)
        # Blit the text.
        txt_x = self.rect.x + (self.rect.width - self.txt_surface.get_width()) / 2
        txt_y = self.rect.y + (self.rect.height - self.txt_surface.get_height()) / 2
        self.screen.blit(self.txt_surface, (txt_x, txt_y))

    def draw(self):

        if self.blink:

            self.draw_button()
            self.active = False
            self.color = COLOR_INACTIVE

        else:

            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
            self.draw_button()
        