import ctypes
from datetime import datetime
import i18n
import uuid
import tkinter.messagebox
from tkinter import *
from tkinter.simpledialog import askstring
from typing import List

from Modules.SaveLoadModule import SaveLoadModule
from Models.Enums.CameraMode import CAMERA_MODE
from Models.Enums.GameMode import GAME_MODE
from Models.Enums.Screen import SCREEN
from Models.Path.Path import Path
from Models.Path.Point import Point
from Models.Path.RenamedPath import RenamedPath
from Models.SavedData.SavedRow import SavedRow
from Models.SettingsTransitionData import SettingsTransitionData
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

    def launch(self, camera_mode:CAMERA_MODE, settings_transition_data:SettingsTransitionData=None):
        """
        Parameters
        ----------
        camera_mode : CAMERA_MODE (GAME / SETTINGS)
            current camera mode
        settings_transition_data : SettingsAndPathData (Used in SETTINGS mode)
            a class instance used to transfer data between SettingsScreen, PathsScreen & CameraScreen in Settings (None if Game mode)
        """

        self.camera_mode = camera_mode

        self.buttons = {
            0: ControlBarButton("↑", self.up_btn_pressed),
            1: ControlBarButton("↓", self.down_btn_pressed),
        } 

        if self.camera_mode == CAMERA_MODE.GAME:
            self.saved_rows = self.save_load_module.load_path_data()
            self.change_title(i18n.t('t.select_path'))
            self.buttons[3] = ControlBarButton(i18n.t('t.enter'), self.enter_btn_pressed)
            self.buttons[9] = ControlBarButton(i18n.t('t.home'), lambda: self.navigate(SCREEN.HOME), bg=THEME_COLOR_PURPLE)

        elif self.camera_mode == CAMERA_MODE.SETTINGS:
            self.settings_transition_data = settings_transition_data
            self.saved_rows = settings_transition_data.saved_rows
            self.change_title(f"{i18n.t('t.select_path')} ({i18n.t('t.configuration')})")
            self.buttons[3] = ControlBarButton(i18n.t('t.edit'), self.enter_btn_pressed)
            self.buttons[5] = ControlBarButton(i18n.t('t.add'), self.add_btn_pressed)
            self.buttons[6] = ControlBarButton(i18n.t('t.rename'), self.rename_btn_pressed)
            self.buttons[7] = ControlBarButton(i18n.t('t.delete'), self.delete_btn_pressed)
            self.buttons[9] = ControlBarButton(i18n.t('t.done'), lambda: self.navigate(SCREEN.SETTINGS, settings_transition_data=self.settings_transition_data), bg=THEME_COLOR_PURPLE)

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
            if self.camera_mode == CAMERA_MODE.GAME:
                self.navigate(SCREEN.CAMERA, camera_mode=CAMERA_MODE.GAME, path=selected_path)
            elif self.camera_mode == CAMERA_MODE.SETTINGS:
                self.navigate(SCREEN.CAMERA, camera_mode=CAMERA_MODE.SETTINGS, path=selected_path, settings_transition_data=self.settings_transition_data)


    def path_double_clicked(self, _):
        self.enter_btn_pressed()


    # Button Methods (Settings)

    def add_btn_pressed(self):
        new_name = askstring(i18n.t('t.rename_path'), i18n.t('t.what_is_the_name_of_new_path?'))
        if self.check_is_new_path_name_valid(new_name) == False:
            return
        new_path = Path(id=uuid.uuid1(), created_timestamp=datetime.today().timestamp(), name=new_name, game_mode=GAME_MODE.OBSTACLE, points=[])
        self.navigate(SCREEN.CAMERA, camera_mode=CAMERA_MODE.SETTINGS, path=new_path, settings_transition_data=self.settings_transition_data)


    def delete_btn_pressed(self):
        result = ctypes.windll.user32.MessageBoxW(None, i18n.t('t.confirm_delete_path'), i18n.t('t.alert'), 1)
        if result == 1:
            # User pressed ok
            selected_path = self.get_selected_path()
            if selected_path:
                new_path_data: List[SavedRow] = []
                for row in self.saved_rows:
                    if row.path_id != selected_path.id:
                        new_path_data.append(row)
                self.saved_rows = new_path_data
                self.settings_transition_data.saved_rows = new_path_data
                self.gui_update()


    def rename_btn_pressed(self):
        selected_path = self.get_selected_path()
        if selected_path:
            new_name = askstring(i18n.t('t.rename_path'), i18n.t('t.what_is_the_name_of_new_path?'))
            if self.check_is_new_path_name_valid(new_name) == False:
                return
            for row in self.saved_rows:
                if row.path_id == selected_path.id:
                    row.path_name = new_name
            self.settings_transition_data.renamed_paths.append(RenamedPath(old_name=selected_path.name, new_name=new_name))
            self.gui_update()


    def check_is_new_path_name_valid(self, new_name) -> bool:
        if new_name is None or new_name == '':
            tkinter.messagebox.showwarning(title=i18n.t('t.warning'), message=i18n.t('t.invalid_path'))
            return False
        for row in self.saved_rows:
            if row.path_name == new_name:
                tkinter.messagebox.showwarning(title=i18n.t('t.warning'), message=i18n.t('t.invalid_path'))
                return False
        return True


    # Other Methods

    def get_selected_path(self) -> Path:
        if len(self.path_listbox.curselection()) != 0:
            path_name: str = self.path_listbox.get(self.path_listbox.curselection()[0]).split(" (")[0]
            path_id: str = None
            path_game_mode: GAME_MODE = None
            points: list[Point] = []
            for row in self.saved_rows:
                if path_name == str(row.path_name):
                    path_id = row.path_id
                    path_created_timestamp = row.path_created_timestamp
                    path_game_mode = row.path_game_mode
                    points.append(Point(x=row.point_x, y=row.point_y, is_good=row.point_is_good, order=row.point_order, alphabet=row.point_alphabet))
            if path_id and path_game_mode:
                return Path(
                    id=path_id,
                    created_timestamp=path_created_timestamp,
                    name=path_name,
                    game_mode=path_game_mode,
                    points=points
                )
        return None


    # GUI Methods

    def gui_set(self):
        self.path_listbox.place(x=CONTROL_BAR_WIDTH/2, relx=0.3, relwidth=0.4, relheight=1.0)


    def gui_update(self):
        self.path_listbox.delete(0, END)
        paths: List[Path] = []
        for row in self.saved_rows:
            path = Path(id=row.path_id, name=row.path_name, game_mode=row.path_game_mode, points=[], created_timestamp=row.path_created_timestamp)
            paths.append(path)

        # Sort By Path Created Time (Descending)
        paths.sort(key=self.get_path_created_timestamp, reverse=True)

        path_names: List[str] = []
        for path in paths:
            gamemode_str = i18n.t(f't.game_mode_{str(path.game_mode.value)}')
            name = f"{path.name} ({gamemode_str})"
            # Ensure there is no repeated name
            if path_names.count(name) == 0:
                path_names.append(name)
        for path_name in path_names:
            self.path_listbox.insert(END, path_name)


    def get_path_created_timestamp(self, path: Path) -> float:
        return path.created_timestamp