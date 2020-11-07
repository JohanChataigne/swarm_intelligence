import pygame as pg

pg.init()
COLOR_INACTIVE = pg.Color((0, 0, 0))
COLOR_ACTIVE = pg.Color((0, 255, 0))
FONT = pg.font.Font(None, 32)


class InputBox:

    def __init__(self, x: int, y: int, w: int, h: int, screen, max_val: float, except_val: float, cast: type, text='', min_width=100, writeable=True):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False
        self.screen = screen
        self.max_val = max_val
        self.except_val = except_val
        self.cast = cast
        self.min_width = min_width
        self.writeable = writeable

    def updateText(self, text: str):
        self.text = text
        self.txt_surface = FONT.render(self.text, True, COLOR_INACTIVE)

    # Try to cast 'try_val' with cast() and assign it to var, or 'except_val' if it fails
    def try_except_cast(self):
        try:
            ret = self.cast(self.text)
            if ret > self.max_val:
                ret = self.max_val
                self.updateText(str(ret))

        except ValueError:
            ret = self.except_val
        
        return ret

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
                self.updateText(str(self.try_except_cast()))

            elif event.type == pg.KEYDOWN and self.active:
                if event.key == pg.K_RETURN:
                    self.active = False
                    self.text = str(self.try_except_cast())
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == pg.K_SEMICOLON:
                    self.text += '.'
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