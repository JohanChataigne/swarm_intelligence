import pygame as pg

pg.init()
COLOR_INACTIVE = pg.Color((180, 180, 180))
COLOR_ACTIVE = pg.Color((100, 100, 100))
COLOR_TEXT = pg.Color((0, 0, 0))
FONT = pg.font.Font(None, 25)


class InputButton:

    def __init__(self, x, y, w, h, screen, text='', active=False, blink=False):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.screen = screen
        self.text = text
        self.active = active
        self.blink = blink
        self.blinking = 0
        self.txt_surface = FONT.render(text, True, COLOR_TEXT)

    def activate(self, buttons):

        self.active = True
        self.color = COLOR_ACTIVE

        if self.blink:
            self.blinking = 1
        
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
        #width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = self.txt_surface.get_width()+10

    def draw(self):

        if self.blink:

            if self.blinking == 0:
                self.active = False
                self.color = COLOR_INACTIVE

                # Blit the rect.
                pg.draw.rect(self.screen, self.color, self.rect)
                # Blit the text.
                txt_x = self.rect.x + (self.rect.width - self.txt_surface.get_width()) / 2
                txt_y = self.rect.y + (self.rect.height - self.txt_surface.get_height()) / 2
                self.screen.blit(self.txt_surface, (txt_x, txt_y))

            else:
                self.blinking -= 1
                # Blit the rect.
                pg.draw.rect(self.screen, self.color, self.rect)
                # Blit the text.
                txt_x = self.rect.x + (self.rect.width - self.txt_surface.get_width()) / 2
                txt_y = self.rect.y + (self.rect.height - self.txt_surface.get_height()) / 2
                self.screen.blit(self.txt_surface, (txt_x, txt_y))

            
            
        else:
            # Blit the rect.
            pg.draw.rect(self.screen, self.color, self.rect)
            # Blit the text.
            txt_x = self.rect.x + (self.rect.width - self.txt_surface.get_width()) / 2
            txt_y = self.rect.y + (self.rect.height - self.txt_surface.get_height()) / 2
            self.screen.blit(self.txt_surface, (txt_x, txt_y))
        