import ctypes
import i18n
from tkinter import *
from tkinter.simpledialog import askstring

from Models.Enums.CameraMode import CAMERA_MODE
from Models.Enums.CameraOrientation import CAMERA_ORIENTATION
from Models.Enums.CameraState import CAMERA_STATE
from Models.Enums.GameMode import GAME_MODE
from Models.Enums.Screen import SCREEN
from Models.Path.Path import Path
from Models.Path.Point import Point
from Models.Resolution import Resolution
from Models.SavedData.SavedRow import SavedRow
from Models.SettingsTransitionData import SettingsTransitionData
from Modules.PoseDetectionModule import PoseDetectionModule
from Modules.SaveLoadModule import SaveLoadModule
from Utilities.Constants import *
from Widgets.ControlBarButton import ControlBarButton

class CameraScreen(Frame):

    def __init__(self, *arg, view_size: Resolution, navigate, change_title, change_buttons, **kwargs):
        Frame.__init__(self, *arg, **kwargs)
        
        self.view_size = view_size

        self.navigate_after_stop_camera = navigate
        self.change_title = change_title
        self.change_buttons = change_buttons

        self.background_view = Label(self, bg='black')
        self.camera_view = Label(self)

        self.distance_angle_label = Label(self, font=(FONT_FAMILY, TITLE_FONT_SIZE), bg=THEME_COLOR)
        self.status_label = Label(self, font=(FONT_FAMILY, TITLE_FONT_SIZE), bg=THEME_COLOR)
        # self.countdown_label = Label(self, font=(FONT_FAMILY, COUNTDOWN_FONT_SIZE), borderwidth=5, relief='solid', bg=THEME_COLOR)
        # self.timer_label = Label(self, font=(FONT_FAMILY, TITLE_FONT_SIZE), bg=THEME_COLOR)
        # self.progress_label = Label(self, font=(FONT_FAMILY, TITLE_FONT_SIZE), bg=THEME_COLOR)
        self.reminder_label = Label(self, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE), bg=THEME_COLOR)

        self.gui_set()

        self.save_load_module = SaveLoadModule()
        self.pose_detection_module = PoseDetectionModule()
        
#         # self.countdown = None
#         # self.timer = None


    # Navigation Methods

    def launch(self, camera_mode:CAMERA_MODE, path:Path=None, settings_transition_data:SettingsTransitionData=None):
        """
        Parameters
        ----------
        camera_mode : CAMERA_MODE
            current camera mode (GAME / SETTINGS)
        path : SavedPath (Used in GAME / SETTINGS mode)
            current path information
        points : list[SavedPoint] (Used in GAME / SETTINGS mode)
            a list of points for this path
        settings_transition_data : SettingsAndPathData (Used in SETTINGS mode)
            a class instance used to transfer data between SettingsScreen, PathsScreen & CameraScreen in Settings
        """

        i18n.set('locale', self.save_load_module.load_locale())
        self.change_title(i18n.t('t.camera'))
        self.camera_mode = camera_mode

        if self.camera_mode == CAMERA_MODE.NORMAL:
            self.settings = self.save_load_module.load_settings()
            self.camera_view.bind("<ButtonRelease-1>", self.normal_screen_pressed_left)

        elif self.camera_mode == CAMERA_MODE.GAME:
            self.settings = self.save_load_module.load_settings()
            self.path = path
            self.points = path.points
            if DEBUG_MODE:
                self.camera_view.bind("<B1-Motion>", self.debug_game_screen_moved)
                self.camera_view.bind("<ButtonRelease-1>", self.debug_game_screen_pressed_left)

        elif self.camera_mode == CAMERA_MODE.SETTINGS:
            self.settings_transition_data = settings_transition_data
            self.settings = self.settings_transition_data.settings
            self.path = path
            self.points = path.points
            self.camera_view.bind("<ButtonRelease-1>", self.settings_screen_pressed_left)
            self.camera_view.bind("<ButtonRelease-3>", self.settings_screen_pressed_right)

        self.gui_buttons_set()

        # Test camera with camera number stored in settings
        camera_number = self.settings.camera_number
        camera_resolution = self.pose_detection_module.get_camera_resolution(camera_number)
        if camera_resolution is None:
            # Update camera number == 0
            camera_number = 0
            self.settings.update(camera_number=camera_number)
            self.save_load_module.save_settings(self.settings)
            # Test camera with camera number == 0
            camera_resolution = self.pose_detection_module.get_camera_resolution(camera_number)
            if camera_resolution is None:
                # If there is still no camera detected, go back to home view
                ctypes.windll.user32.MessageBoxW(0, i18n.t('t.no_camera_is_detected'), i18n.t('t.camera_is_unavailable'), 0)
                self.navigate(SCREEN.HOME)
                return

        if self.settings.camera_orientation_mode == CAMERA_ORIENTATION.LEFT or self.settings.camera_orientation_mode == CAMERA_ORIENTATION.RIGHT:
            camera_resolution.exchange_width_height()

        camera_view_size = self.gui_camera_view_set(camera_resolution=camera_resolution)
        self.pose_detection_module.set_camera_input(self.camera_view, camera_view_size=camera_view_size, camera_number=camera_number, camera_resolution=camera_resolution, settings=self.settings)

        if self.camera_mode == CAMERA_MODE.NORMAL:
            self.normal_change_camera_state(CAMERA_STATE.PLAYING)
            self.pose_detection_module.camera_input()

        if self.camera_mode == CAMERA_MODE.GAME:
            gamemode_str = i18n.t(f't.game_mode_{str(self.path.game_mode.value)}')
            self.change_title(f"{self.path.name} ({gamemode_str})")
            self.game_change_camera_state(CAMERA_STATE.PLAYING)
            self.pose_detection_module.game_start(path=self.path, progress_callback=self.game_progress_update)

        elif self.camera_mode == CAMERA_MODE.SETTINGS:
            gamemode_str = i18n.t(f't.game_mode_{str(self.path.game_mode.value)}')
            self.change_title(f"{self.path.name} ({gamemode_str})")
            self.pose_detection_module.settings_start(path=self.path)
#         self.clear_labels()


    def navigate(self, view, **kwargs):
        self.pose_detection_module.stop_camera_input()
        # if self.countdown is not None:
        #     self.countdown.reset()
        # if self.timer is not None:
        #     self.timer.reset()
        self.navigate_after_stop_camera(view, **kwargs)


    # Methods (for ALL Camera Mode)

#     def show_danger_alerts(self, show):
#         if show:
#             self.reminder_label.place(relx=0.5, rely=1.0, y=-10, width=600, anchor=S)
#         else:
#             self.reminder_label.place_forget()


    # Methods (for NORMAL Camera Mode)

    def normal_change_camera_state(self, state):
        self.normal_clear_camera_state()
        if state == CAMERA_STATE.PLAYING:
            self.buttons[0] = ControlBarButton(i18n.t('t.pause'), lambda: self.normal_change_camera_state(CAMERA_STATE.PAUSE))
            self.buttons[1] = ControlBarButton(i18n.t('t.record'), lambda: self.normal_change_camera_state(CAMERA_STATE.RECORDING))
        elif state == CAMERA_STATE.PAUSE:
            self.status_label.config(text=f"{i18n.t('t.pause')}...")
            self.status_label.place(x=15, y=15)
            self.buttons[0] = ControlBarButton(i18n.t('t.play'), lambda: self.normal_change_camera_state(CAMERA_STATE.PLAYING))
            self.buttons[1] = ControlBarButton(i18n.t('t.clear'), lambda: self.normal_clear_btn_pressed())
        elif state == CAMERA_STATE.RECORDING:
            self.status_label.config(text=f"{i18n.t('t.recording')}...")
            self.status_label.place(x=15, y=15)
            self.buttons[1] = ControlBarButton(i18n.t('t.stop_recording'), lambda: self.normal_change_camera_state(CAMERA_STATE.PLAYING))
        self.pose_detection_module.change_camera_state(state)
        self.camera_state = state
        self.change_buttons(self.buttons)


    def normal_clear_camera_state(self):
        self.buttons.pop(0, None)
        self.buttons.pop(1, None)
        self.distance_angle_label.place_forget()


    def normal_screen_pressed_left(self, event):
        if self.camera_state == CAMERA_STATE.PAUSE:
            point = Point(x=event.x, y=event.y)
            calculationResult = self.pose_detection_module.normal_pause_tap_on_screen(point)
            if calculationResult.distance:
                self.distance_angle_label.config(text=i18n.t('t.distance')+": {:.2f} m".format(calculationResult.distance))
                self.distance_angle_label.place(relx=0.5, y=15, anchor=N)                
            elif calculationResult.angle:
                self.distance_angle_label.config(text=i18n.t('t.angle')+":{:.2f}".format(calculationResult.angle))
                self.distance_angle_label.place(relx=0.5, y=15, anchor=N)
            else:
                self.distance_angle_label.place_forget()


    def normal_clear_btn_pressed(self):
        self.pose_detection_module.normal_pause_clear_all_dots()
        self.distance_angle_label.place_forget()


    # Methods (for GAME Camera Mode)

    def game_change_camera_state(self, state):
        self.game_clear_camera_state()
        if state == CAMERA_STATE.PLAYING:
            self.buttons[2] = ControlBarButton(i18n.t('t.record'), lambda: self.game_change_camera_state(CAMERA_STATE.RECORDING))
        elif state == CAMERA_STATE.RECORDING:
            self.status_label.config(text=f"{i18n.t('t.recording')}...")
            self.status_label.place(x=15, y=15)
            self.buttons[2] = ControlBarButton(i18n.t('t.stop_recording'), lambda: self.game_change_camera_state(CAMERA_STATE.PLAYING))
        self.pose_detection_module.change_camera_state(state)
        self.camera_state = state
        self.change_buttons(self.buttons)


    def game_clear_camera_state(self):
        self.buttons.pop(2, None)
        self.status_label.place_forget()


    def game_progress_update(self, touched, all):
        if self.path.game_mode == GAME_MODE.OBSTACLE or self.path.game_mode == GAME_MODE.SEQUENCE:
            self.progress_label.config(text=f"{touched}/{all}")
            if touched == all:
                self.finish_btn_pressed()
        elif self.path.game_mode == GAME_MODE.ALPHABET:
            self.progress_label.config(text=f"{touched}")


    def game_finish_btn_pressed(self):
        pass
        # result = self.pose_detection_module.game_finish()
        # result.update_time(self.timer_label['text'])
        # self.navigate(SCREEN.RESULT, result=result, gamemode=self.path.game_mode)


    def game_leave_btn_pressed(self):
        self.navigate(SCREEN.PATHS, camera_mode=CAMERA_MODE.GAME)


#     # Timer Methods (Game)

#     def countdown_update(self, time):
#         self.countdown_label.config(text=time[-1])


#     def countdown_finish(self):
#         self.countdown_label.place_forget()
#         self.timer = Timer(self.timer_update)
#         self.timer.start()
#         self.timer_label.place(relx=1.0, width=200, height=CONTROL_BAR_BUTTON_HEIGHT, anchor=NE)
#         self.progress_label.place(y=CONTROL_BAR_BUTTON_HEIGHT, relx=1.0, width=200, height=CONTROL_BAR_BUTTON_HEIGHT, anchor=NE)


#     def timer_update(self, time):
#         self.timer_label.config(text=time)


#     def clear_labels(self):
#         self.countdown_label.place_forget()
#         self.reminder_label.place_forget()
#         self.timer_label.place_forget()
#         self.progress_label.place_forget()


    # Methods (for SETTINGS Camera Mode)

    def settings_screen_pressed_left(self, event):
        if self.path.game_mode == GAME_MODE.OBSTACLE:
            good_point = Point(x=event.x, y=event.y, is_good=True)
            self.pose_detection_module.settings_screen_pressed(camera_point=good_point)

        elif self.path.game_mode == GAME_MODE.SEQUENCE:
            point = Point(x=event.x, y=event.y)
            self.pose_detection_module.settings_screen_pressed(camera_point=point)

        elif self.path.game_mode == GAME_MODE.ALPHABET:
            alphabet = askstring(i18n.t('t.alphabet'), i18n.t('t.input_alphabet'))
            if alphabet is None or len(alphabet) > 1:
                ctypes.windll.user32.MessageBoxW(0, i18n.t('t.input_alphabet'), i18n.t('t.error'), 0)
                return
            alphabet = alphabet.upper()
            if ord(alphabet) < ord('A') or ord(alphabet) > ord('Z'):
                ctypes.windll.user32.MessageBoxW(0, i18n.t('t.input_alphabet'), i18n.t('t.error'), 0)
                return
            point = Point(x=event.x, y=event.y, alphabet=alphabet)
            self.pose_detection_module.settings_screen_pressed(camera_point=point)


    def settings_screen_pressed_right(self, event):
        if self.camera_mode == CAMERA_MODE.SETTINGS and self.path.game_mode == GAME_MODE.OBSTACLE:
            bad_point = Point(x=event.x, y=event.y, is_good=False)
            self.pose_detection_module.settings_screen_pressed(camera_point=bad_point)


    def settings_change_game_mode_btn_pressed(self):
        if self.path.game_mode == GAME_MODE.OBSTACLE:
            self.path.game_mode = GAME_MODE.SEQUENCE
        elif self.path.game_mode == GAME_MODE.SEQUENCE:
            self.path.game_mode = GAME_MODE.ALPHABET
        elif self.path.game_mode == GAME_MODE.ALPHABET:
            self.path.game_mode = GAME_MODE.OBSTACLE
        gamemode_str = i18n.t(f't.game_mode_{str(self.path.game_mode.value)}')
        self.change_title(f"{self.path.name} ({gamemode_str})")
        # Clear all points when change game mode
        self.path.settings_update_points(points=[])
        self.pose_detection_module.settings_start(path=self.path)


    def settings_undo_btn_pressed(self):
        self.pose_detection_module.settings_undo()


    def settings_redo_btn_pressed(self):
        self.pose_detection_module.settings_redo()


    def settings_clear_all_points_btn_pressed(self):
        self.pose_detection_module.settings_clear_all_points()


    def settings_cancel_btn_pressed(self):
        self.navigate(SCREEN.PATHS, camera_mode=CAMERA_MODE.SETTINGS, settings_transition_data=self.settings_transition_data)


    def settings_confirm_btn_pressed(self):
        self.path, new_path_image = self.pose_detection_module.settings_done()

        if not self.settings_confirm_validation(path=self.path):
            return

        new_saved_rows: list[SavedRow] = self.settings_transition_data.saved_rows.copy()

        # Remove all points of this path
        for row in self.settings_transition_data.saved_rows:
            if row.path_id == self.path.id:
                new_saved_rows.remove(row)
        # Add new points for this path
        new_saved_rows.extend(self.path.to_saved_rows())

        new_updated_path_images = self.settings_transition_data.updated_path_images + [new_path_image]
        new_settings_transition_data = SettingsTransitionData(settings=self.settings, saved_rows=new_saved_rows, renamed_paths=self.settings_transition_data.renamed_paths, updated_path_images=new_updated_path_images)

        self.navigate(SCREEN.PATHS, camera_mode=CAMERA_MODE.SETTINGS, settings_transition_data=new_settings_transition_data)


    def settings_confirm_validation(self, path: Path) -> bool:
        """
        Test if this path is valid to be saved.
        Return true if valid, false otherwise.
        """
        if path.game_mode == GAME_MODE.OBSTACLE:
            if len(path.good_points) == 0:
                # If there is no good point, show error message
                ctypes.windll.user32.MessageBoxW(0, i18n.t('t.error_path'), i18n.t('t.error'), 0)
                return False
        elif path.game_mode == GAME_MODE.SEQUENCE:
            if len(path.points) == 0:
                # If there is no point, show error message
                ctypes.windll.user32.MessageBoxW(0, i18n.t('t.error_path'), i18n.t('t.error'), 0)
                return False
        elif path.game_mode == GAME_MODE.ALPHABET:
            if len(path.points) == 0:
                # If there is no point, show error message
                ctypes.windll.user32.MessageBoxW(0, i18n.t('t.error_path'), i18n.t('t.error'), 0)
                return False
        return True


    # GUI Methods

    def gui_camera_view_set(self, camera_resolution: Resolution) -> Resolution:
        background_view_ratio = self.view_size.width / self.view_size.height
        camera_view_ratio = camera_resolution.width / camera_resolution.height
        if background_view_ratio > camera_view_ratio:
            # The width of background_view is larger than the width of camera_view
            camera_view_height = self.view_size.height
            camera_view_width = int(self.view_size.height * camera_view_ratio)
        else:
            # The height of background_view is larger than the height of camera_view
            camera_view_width = self.view_size.width
            camera_view_height = int(self.view_size.width / camera_view_ratio)
        self.camera_view.place(relx=0.5, rely=0.5, width=camera_view_width, height=camera_view_height, anchor=CENTER)
        camera_view_size = Resolution(width=camera_view_width, height=camera_view_height)
        return camera_view_size


    def gui_buttons_set(self):
        if self.camera_mode == CAMERA_MODE.NORMAL:
            self.buttons = {
                0: ControlBarButton(i18n.t('t.pause'), lambda: self.normal_change_camera_state(CAMERA_STATE.PAUSE)),
                1: ControlBarButton(i18n.t('t.record'), lambda: self.normal_change_camera_state(CAMERA_STATE.RECORDING)),
                9: ControlBarButton(i18n.t('t.home'), lambda: self.navigate(SCREEN.HOME), THEME_COLOR_PINK)
            }
            self.reminder_label.config(text=f"{i18n.t('t.DANGER_ALERT_Two_hands_are_outside_feet_area')}")
        
        elif self.camera_mode == CAMERA_MODE.GAME:
            self.buttons = {
                0: ControlBarButton(i18n.t('t.finish'), self.game_finish_btn_pressed),
                2: ControlBarButton(i18n.t('t.record'), lambda: self. game_change_camera_state(CAMERA_STATE.RECORDING)),
                9: ControlBarButton(i18n.t('t.leave'), self.game_leave_btn_pressed, THEME_COLOR_PINK)
            }
            # self.countdown = Timer(self.countdown_update, True, 6, self.countdown_finish)
            # self.countdown.start()
            # self.countdown_label.place(relx=0.5, rely=0.5, width=400, height=400, anchor=CENTER)
            # self.reminder_label.config(text=f"{i18n.t('t.DANGER_ALERT_Two_hands_are_outside_feet_area')}")

            # TODO: Projector Mode
            # A new window is created in a separate monitor for projector to project on the surface of rock climbing wall
            # projector_view = Toplevel(self)
            # projector_view.overrideredirect(True)
            # projector_view.geometry('%dx%d+%d+%d'%(1920,1080,0,-1080))
            # projector_view.attributes('-fullscreen', False)
            # projector_view.title("New Window")
            # print(WINDOW_HEIGHT, WINDOW_WIDTH)
            # projector_view.pose_detection.cameraInput()

        elif self.camera_mode == CAMERA_MODE.SETTINGS:
            self.buttons = {
                0: ControlBarButton(i18n.t('t.change_game_mode'), self.settings_change_game_mode_btn_pressed),
                2: ControlBarButton(i18n.t('t.undo'), self.settings_undo_btn_pressed),
                3: ControlBarButton(i18n.t('t.redo'), self.settings_redo_btn_pressed),
                4: ControlBarButton(i18n.t('t.clear_all_points'), self.settings_clear_all_points_btn_pressed),
                8: ControlBarButton(i18n.t('t.cancel'), self.settings_cancel_btn_pressed, THEME_COLOR_PINK),
                9: ControlBarButton(i18n.t('t.confirm'), self.settings_confirm_btn_pressed, THEME_COLOR_PURPLE)
            }
            self.reminder_label.config(text=f"""{i18n.t('t.press_left_mouse_button_for_new_touch_point')}
{i18n.t('t.press_right_mouse_button_for_new_avoid_point')}""")
            self.reminder_label.place(relx=0.5, rely=1.0, y=-10, width=600, anchor=S)

        self.change_buttons(self.buttons)
        
        
    def gui_set(self):
        self.background_view.place(relwidth=1.0, relheight=1.0)


    # Debug Methods (for GAME Camera Mode)

    def debug_game_screen_moved(self, event):
        point = Point(x=event.x, y=event.y)
        self.pose_detection_module.game_simulate_body_point(camera_point=point)


    def debug_game_screen_pressed_left(self, _):
        if DEBUG_MODE:
            self.pose_detection_module.game_simulate_body_point()
