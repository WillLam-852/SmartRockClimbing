import ctypes
import i18n
import os
import sys
import PIL.Image, PIL.ImageTk
from tkinter import *
from Models.Camera.Resolution import Resolution
from Models.Enums.CameraMode import CAMERA_MODE

from Widgets.ControlBarButton import ControlBarButton
from Modules.SaveLoadModule import SaveLoadModule
from Models.Enums.Screen import SCREEN
from Utilities.Constants import *
from Utilities.OpenFile import open_file

class HomeScreen(Frame):

    def __init__(self, *arg, view_size: Resolution, navigate, change_title, change_buttons, exit, **kwargs):
        Frame.__init__(self, *arg, **kwargs)
        
        self.view_size = view_size

        self.navigate = navigate
        self.change_title = change_title
        self.change_buttons = change_buttons

        self.exit = exit

        self.gui_calculate_values()

        self.logo_image = PIL.Image.open(open_file(f"{IMAGE_FILES_LOCATION}Logo.png")).resize((self.logo_image_size, self.logo_image_size), PIL.Image.ANTIALIAS)
        self.logo_image = PIL.ImageTk.PhotoImage(self.logo_image)
        self.logo_label = Label(self, image=self.logo_image, bg=THEME_COLOR_BLUE)
        
        self.name_label = Label(self, font=(FONT_FAMILY, TITLE_FONT_SIZE), bg=THEME_COLOR_BLUE)

        self.save_load_module = SaveLoadModule()
        self.locale = self.save_load_module.load_locale()

        self.gui_set()
        

    # Navigation Methods

    def launch(self):
        self.gui_update()
        

    # Button Methods
    
    def change_locale_btn_pressed(self):
        if self.locale == 'en':
            self.locale = 'ch'
        elif self.locale == 'ch':
            self.locale = 'en'
        i18n.set('locale', self.locale)
        self.save_load_module.save_locale(self.locale)
        self.gui_update()


    def show_restart_alert(self):
        result = ctypes.windll.user32.MessageBoxW(None, i18n.t('t.confirm_restart_program'), i18n.t('t.alert'), 1)
        if result == 1:
            # User pressed ok
            self.exit()
            os.execl(sys.executable, os.path.abspath(__file__), *sys.argv) 


    def show_exit_alert(self):
        result = ctypes.windll.user32.MessageBoxW(None, i18n.t('t.confirm_exit_program'), i18n.t('t.alert'), 1)
        if result == 1:
            # User pressed ok
            self.exit()


    # GUI Methods

    def gui_calculate_values(self):
        self.logo_image_size = int(min(self.view_size.width, self.view_size.height)/3)


    def gui_set(self):
        self.logo_label.place(rely=0.1, relwidth=1.0, height=self.logo_image_size)
        self.name_label.place(rely=0.5, relwidth=1.0, relheight=0.3)


    def gui_update(self):
        i18n.set('locale', self.locale)
        self.change_title(i18n.t('t.home'))
        self.buttons = {
            0: ControlBarButton(i18n.t('t.camera'), lambda: self.navigate(SCREEN.CAMERA)),
            1: ControlBarButton(i18n.t('t.game'), lambda: self.navigate(SCREEN.PATHS, camera_mode=CAMERA_MODE.GAME)),
            # 2: ControlBarButton(i18n.t('t.recordings'), lambda: self.navigate(SCREEN.RECORDINGS)),
            6: ControlBarButton(i18n.t('t.current_locale'), lambda: self.change_locale_btn_pressed()),
            # 7: ControlBarButton(i18n.t('t.settings'), lambda: self.navigate(SCREEN.SETTINGS)),
            8: ControlBarButton(i18n.t('t.restart_program'), self.show_restart_alert, THEME_COLOR_PINK),
            9: ControlBarButton(i18n.t('t.exit_program'), self.show_exit_alert, THEME_COLOR_PINK)
        }
        self.change_buttons(self.buttons)
        self.name_label.config(text=f"{i18n.t('t.school_name')}\n{i18n.t('t.system_name')}")

