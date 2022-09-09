import ctypes
import i18n
import uuid
import tkinter.messagebox
from tkinter import *
from tkinter.simpledialog import askstring
from typing import List

from Modules.SaveLoadModule import SaveLoadModule
from Models.SavedData import SavedData, SavedPath, SavedPoint
from Models.Paths.RenamedPath import RenamedPath
from Models.Enums.Screen import SCREEN
from Models.Enums.CameraMode import CAMERA_MODE
from Models.Enums.GameMode import GAME_MODE
from Widgets.ControlBarButton import ControlBarButton
from Utilities.Constants import *

class PathsScreen(Frame):

    def __init__(self, *arg, view_size, navigate, change_title, change_buttons, **kwargs):
        Frame.__init__(self, *arg, **kwargs)
        
        self.view_size = view_size

        self.navigate = navigate
        self.change_title = change_title
        self.change_buttons = change_buttons

        self.selected_path_name = None

        self.path_listbox = Listbox(self, font=(FONT_FAMILY, HEADING_FONT_SIZE))
        self.path_listbox.bind("<Double-Button-1>", self.path_double_clicked)
        
        self.save_load_module = SaveLoadModule()
        i18n.set('locale', self.save_load_module.load_locale())
        
        self.gui_set()


    # Navigation Methods

    def launch(self, camera_mode:CAMERA_MODE, settings_path_data=[], settings_path_images=[]):
        self.camera_mode = camera_mode

        self.buttons = {
            0: ControlBarButton("↑", self.up_btn_pressed),
            1: ControlBarButton("↓", self.down_btn_pressed),
        }

        if self.camera_mode == CAMERA_MODE.GAME:
            self.path_data = self.save_load_module.load_path_data()
            self.change_title(i18n.t('t.select_path'))
            self.buttons[3] = ControlBarButton(i18n.t('t.enter'), self.enter_btn_pressed)
            self.buttons[9] = ControlBarButton(i18n.t('t.home'), lambda: self.navigate(SCREEN.HOME), THEME_COLOR_PURPLE)

        elif self.camera_mode == CAMERA_MODE.SETTINGS:
            self.path_data = settings_path_data
            self.settings_renamed_paths: list[RenamedPath] = []
            self.settings_path_images = settings_path_images
            self.change_title(f"{i18n.t('t.select_path')} ({i18n.t('t.configuration')})")
            self.buttons[3] = ControlBarButton(i18n.t('t.edit'), self.enter_btn_pressed)
            self.buttons[5] = ControlBarButton(i18n.t('t.add'), self.add_btn_pressed)
            self.buttons[6] = ControlBarButton(i18n.t('t.rename'), self.rename_btn_pressed)
            self.buttons[7] = ControlBarButton(i18n.t('t.delete'), self.delete_btn_pressed)
            self.buttons[9] = ControlBarButton(i18n.t('t.done'), lambda: self.navigate(SCREEN.SETTINGS, path_data=self.path_data, rename_paths=self.settings_renamed_paths, path_images=self.settings_path_images), THEME_COLOR_PURPLE)

        self.change_buttons(self.buttons)
        self.gui_update()


    # Button Methods

    def up_btn_pressed(self):
        if len(self.path_listbox.curselection()) != 0:
            next_listbox_index = self.path_listbox.curselection()[0] - 1
            if next_listbox_index >= 0 :
                self.path_listbox.selection_clear(0, END)
                self.path_listbox.selection_set(next_listbox_index)
        else:
            self.path_listbox.selection_set("end")


    def down_btn_pressed(self):
        if len(self.path_listbox.curselection()) != 0:
            next_listbox_index = self.path_listbox.curselection()[0] + 1
            if next_listbox_index < self.path_listbox.size():
                self.path_listbox.selection_clear(0, END)
                self.path_listbox.selection_set(next_listbox_index)
        else:
            self.path_listbox.selection_set(0)


    def enter_btn_pressed(self):
        selected_path = self.get_selected_path()
        if selected_path:
            points = self.extract_point_list(selected_path.id)
            self.navigate(SCREEN.CAMERA, camera_mode=self.camera_mode, path=selected_path, points=points)


    def path_double_clicked(self, _):
        self.enter_btn_pressed()


    # Button Methods (Settings)

    def add_btn_pressed(self):
        new_name = askstring(i18n.t('t.rename_path'), i18n.t('t.what_is_the_name_of_new_path?'))
        if self.check_is_new_path_name_valid(new_name) == False:
            return
        new_path = SavedPath(id=uuid.uuid1(), name=new_name, gamemode=GAME_MODE.OBSTACLE)
        self.navigate(SCREEN.CAMERA, camera_mode=self.camera_mode, path=new_path, points=[])


    def delete_btn_pressed(self):
        result = ctypes.windll.user32.MessageBoxW(None, i18n.t('t.confirm_delete_path'), i18n.t('t.alert'), 1)
        if result == 1:
            # User pressed ok
            selected_path = self.get_selected_path()
            if selected_path:
                new_path_file: List[SavedData] = []
                for row in self.path_data:
                    if row.path_id != selected_path.id:
                        new_path_file.append(row)
                self.path_data = new_path_file
                self.gui_update()


    def rename_btn_pressed(self):
        selected_path = self.get_selected_path()
        if selected_path:
            new_name = askstring(i18n.t('t.rename_path'), i18n.t('t.what_is_the_name_of_new_path?'))
            if self.check_is_new_path_name_valid(new_name) == False:
                return
            for row in self.path_data:
                if row.path_id == selected_path.id:
                    row.path_name = new_name
            self.settings_renamed_paths.append(
                RenamedPath(old_name=selected_path.name, new_name=new_name)
            )
            self.gui_update()


    def check_is_new_path_name_valid(self, new_name) -> bool:
        if new_name is None or new_name == '':
            tkinter.messagebox.showwarning(title=i18n.t('t.warning'), message=i18n.t('t.invalid_path'))
            return False
        for row in self.path_data:
            if row.path_name == new_name:
                tkinter.messagebox.showwarning(title=i18n.t('t.warning'), message=i18n.t('t.invalid_path'))
                return False
        return True


    # Other Methods

    def get_selected_path(self) -> SavedPath:
        if len(self.path_listbox.curselection()) != 0:
            path_name = self.path_listbox.get(self.path_listbox.curselection()[0]).split(" (")[0]
            path_id = None
            path_gamemode = None
            for row in self.path_data:
                if path_name == row.path_name:
                    path_id = row.path_name
                    path_gamemode = row.path_gamemode
                    break
            if path_id and path_gamemode:
                return SavedPath(
                    id=path_id,
                    name=path_name,
                    gamemode=path_gamemode
                )
        return None


    def extract_point_list(self, path_id) -> list[SavedPoint]:
        points: list[SavedPoint] = []
        for row in self.path_data:
            if row.path_id == path_id:
                point = SavedPoint(x=row.point_x, y=row.point_y, is_good=row.point_is_good, order=row.point_order, alphabet=row.point_alphabet)
                points.append(point)
        return points


    # GUI Methods

    def gui_set(self):
        self.path_listbox.place(x=CONTROL_BAR_WIDTH/2, relx=0.3, relwidth=0.4, relheight=1.0)


    def gui_update(self):
        self.path_listbox.delete(0, END)
        path_names: List[str] = []
        for row in self.path_data:
            gamemode_str = i18n.t(f't.game_mode_{str(row.path_gamemode.value)}')
            path_names.append(f"{row[1]} ({gamemode_str})")
        path_names = list(set(path_names))
        for path_name in path_names:
            self.path_listbox.insert(END, path_name)
