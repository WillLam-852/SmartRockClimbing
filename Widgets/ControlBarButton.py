from Utilities.Constants import *

class ControlBarButton:
    def __init__(self, text, command, bg=THEME_COLOR_YELLOW):
        self.text = text
        self.command = command
        self.bg = bg