import ctypes
from pprint import isrecursive
import i18n
import gc
from tkinter import *
from Models.Resolution import Resolution
from Models.Enums.CameraMode import CAMERA_MODE

from Models.Enums.Screen import SCREEN
from Models.SettingsTransitionData import SettingsTransitionData
from Modules.SaveLoadModule import SaveLoadModule
from Utilities.OpenFile import open_file
from Utilities.Constants import *
from Widgets.TopBar import TopBar
from Widgets.ControlBar import ControlBar

from Screens.HomeScreen import HomeScreen
from Screens.CameraScreen import CameraScreen
from Screens.PathsScreen import PathsScreen
from Screens.SettingsScreen import SettingsScreen

class SmartRockClimbing:

    def __init__(self):
        self.root = Tk()
        self.root.attributes("-fullscreen", True)
        self.root.bind("<KeyRelease>", self.key_up)
        self.window_size = get_fullscreen_size()
        if DEBUG_MODE:
            self.root.attributes("-fullscreen", False)
            self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
            self.root.resizable(False, False)
            self.window_size = Resolution(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        set_locale()

        self.gui_calculate_values()

        self.top_bar = TopBar(self.root, bg=THEME_COLOR_BLUE)
        self.control_bar = ControlBar(self.root, bg=THEME_COLOR_BLUE)
        self.current_screen = None

        self.gui_set()
        self.is_keypad_reverse = SaveLoadModule().load_settings().is_keypad_reverse

        if DEBUG_MODE:
            self.navigate(SCREEN.HOME)
        else:
            self.navigate(SCREEN.HOME)


    # Navigation Methods

    def navigate(self, screen_to, **kwargs):
        self.reset_screen()
        if screen_to == SCREEN.HOME:
            self.current_screen = HomeScreen(
                self.root, 
                view_size=self.view_size, 
                navigate=self.navigate, 
                change_title=self.change_title, 
                change_buttons=self.change_buttons, 
                exit=self.root.destroy, 
                bg=THEME_COLOR
            )
        elif screen_to == SCREEN.CAMERA:
            self.current_screen = CameraScreen(
                self.root, 
                view_size=self.view_size, 
                navigate=self.navigate, 
                change_title=self.change_title, 
                change_buttons=self.change_buttons, 
                bg=THEME_COLOR
            )
        elif screen_to == SCREEN.PATHS:
            self.current_screen = PathsScreen(
                self.root, 
                view_size=self.view_size, 
                navigate=self.navigate, 
                change_title=self.change_title, 
                change_buttons=self.change_buttons, 
                bg=THEME_COLOR
            )
        # elif screen_to == SCREEN.RESULT:
        #     self.current_screen = self.result_view
        # elif screen_to == SCREEN.RECORDINGS:
        #     self.current_screen = self.recordings_view
        # elif screen_to == SCREEN.VIDEO:
        #     self.current_screen = self.video_view
        elif screen_to == SCREEN.SETTINGS:
            self.current_screen = SettingsScreen(
                self.root, 
                view_size=self.view_size, 
                navigate=self.navigate, 
                change_title=self.change_title, 
                change_buttons=self.change_buttons,
                change_keypad=self.change_keypad,
                bg=THEME_COLOR
            )
        self.current_screen.launch(**kwargs)
        self.current_screen.place(y=TOP_BAR_HEIGHT, width=self.view_size.width, height=self.view_size.height)


    def reset_screen(self):
        if self.current_screen:
            del(self.current_screen)
            gc.collect()


    def change_title(self, title):
        self.top_bar.change_title(title)


    def change_buttons(self, buttons):
        self.control_bar.change_buttons(buttons)


    # Key Press Actions

    def key_up(self, e):
        self.control_bar.invoke_button(e.char, self.is_keypad_reverse)

    def change_keypad(self, is_reverse):
        self.is_keypad_reverse = is_reverse
        self.root.bind("<KeyRelease>", self.key_up)


    # GUI Methods

    def gui_calculate_values(self):
        view_width = self.window_size.width - CONTROL_BAR_WIDTH
        view_height = self.window_size.height - TOP_BAR_HEIGHT
        self.view_size = Resolution(width=view_width, height=view_height)


    def gui_set(self):
        self.top_bar.place(width=self.window_size.width, height=TOP_BAR_HEIGHT)
        self.control_bar.place(x=self.window_size.width-CONTROL_BAR_WIDTH, y=TOP_BAR_HEIGHT, width=CONTROL_BAR_WIDTH, height=self.window_size.height-TOP_BAR_HEIGHT)



def get_fullscreen_size() -> Resolution:
    user32 = ctypes.windll.user32
    screensize = Resolution(width=user32.GetSystemMetrics(0), height=user32.GetSystemMetrics(1))
    return screensize


def set_locale():
    i18n.set('file_format', 'json')
    i18n.load_path.append(open_file(TRANSLATION_FILES_LOCATION))
    i18n.set('fallback', 'ch')


if __name__ == '__main__':
    smart_rock_climbing = SmartRockClimbing()
    mainloop()