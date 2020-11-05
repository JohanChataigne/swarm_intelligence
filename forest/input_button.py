import pygame as pg

pg.init()
COLOR_INACTIVE = pg.Color((180, 180, 180))
COLOR_ACTIVE = pg.Color((100, 100, 100))
COLOR_TEXT = pg.Color((0, 0, 0))
FONT = pg.font.Font(None, 25)


class InputButton:

    def __init__(self, x, y, w, h, screen, text='', active=False):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, COLOR_TEXT)
        self.active = active
        self.screen = screen

    def activate(self, buttons):

        self.active = True
        for but in [b for b in buttons.values() if b != self]:
            but.active = False

    def handle_event(self, event, buttons):
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.activate(buttons)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self):
        self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        # Blit the rect.
        pg.draw.rect(self.screen, self.color, self.rect)
        # Blit the text.
        self.screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        