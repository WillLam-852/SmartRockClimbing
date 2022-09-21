import ctypes
import i18n
import copy
from tkinter import *
from Models.Enums.CameraMode import CAMERA_MODE

from Models.Resolution import Resolution
from Models.Enums.CameraOrientation import CAMERA_ORIENTATION
from Models.Enums.Screen import SCREEN
from Models.Enums.SensitivityLevel import SENSITIVITY_LEVEL
from Models.SettingsTransitionData import SettingsTransitionData
from Modules.SaveLoadModule import SaveLoadModule
from Modules.PoseDetectionModule import PoseDetectionModule
from Modules.SoundModule import SoundModule
from Widgets.ControlBarButton import ControlBarButton
from Utilities.Constants import *

class SettingsScreen(Frame):

    def __init__(self, *arg, view_size: Resolution, navigate, change_title, change_buttons, change_keypad, **kwargs):
        Frame.__init__(self, *arg, **kwargs)
        
        self.view_size = view_size

        self.navigate_after_stop_camera = navigate
        self.change_title = change_title
        self.change_buttons = change_buttons
        self.change_keypad = change_keypad

        self.background_view_size = Resolution(width=self.view_size.width*0.7, height=view_size.height)
        self.current_page = 0

        self.is_distance_calibration_shown = False

        self.save_load_module = SaveLoadModule()
        self.pose_detection_module = PoseDetectionModule()

        self.background_view = Label(self, font=(FONT_FAMILY, TITLE_FONT_SIZE), fg='white', bg='black')
        self.camera_view = Label(self)
        self.label_view = Label(self, bg=THEME_COLOR_BLUE)

        self.danger_alert_label = Label(self.label_view, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE), bg=THEME_COLOR_BLUE)
        self.sensitivity_label = Label(self.label_view, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE), bg=THEME_COLOR_BLUE)

        self.camera_number_label = Label(self.label_view, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE), bg=THEME_COLOR_BLUE)
        self.camera_orientation_label = Label(self.label_view, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE), bg=THEME_COLOR_BLUE)        
        self.camera_mirror_label = Label(self.label_view, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE), bg=THEME_COLOR_BLUE)
        self.distance_calibration_actual_value_label = Label(self.label_view, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE), bg=THEME_COLOR_BLUE)
        self.ground_calibration_actual_position_label = Label(self.label_view, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE), bg=THEME_COLOR_BLUE)
        self.reverse_keypad_label = Label(self.label_view, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE), bg=THEME_COLOR_BLUE)
        
        self.gui_set()


    # Navigation Methods

    def launch(self, settings_transition_data:SettingsTransitionData=None):
        """
        Parameters
        ----------
        settings_transition_data : SettingsAndPathData
            a class instance used to transfer data between SettingsScreen, PathsScreen & CameraScreen in Settings (None if from HomeScreen)
        """
        i18n.set('locale', self.save_load_module.load_locale())
        self.old_settings = self.save_load_module.load_settings()
            
        if settings_transition_data:
            self.settings_transition_data = settings_transition_data
        else:
            self.settings_transition_data = SettingsTransitionData(settings=copy.deepcopy(self.old_settings), saved_rows=self.save_load_module.load_path_data(), renamed_paths=[], updated_path_images=[])
        
        self.is_camera_detected = self.restart_camera()
        self.current_page = 0
        self.gui_update()


    def navigate(self, view, **kwargs):
        if self.is_camera_detected:
            self.pose_detection_module.stop_camera_input()
        self.navigate_after_stop_camera(view, **kwargs)


    def restart_camera(self, camera_number=None) -> bool:
        try:
            self.pose_detection_module.stop_camera_input()
        except:
            print("ERROR: There is no pose_detection_module")
        self.pose_detection_module = PoseDetectionModule()
        if camera_number:
            self.camera_resolution = self.pose_detection_module.get_camera_resolution(camera_number)
            set_camera_number = camera_number
        else:
            self.camera_resolution = self.pose_detection_module.get_camera_resolution(self.settings_transition_data.settings.camera_number)
            set_camera_number = self.settings_transition_data.settings.camera_number
        if self.camera_resolution:
            camera_view_size = self.gui_camera_view_set(camera_resolution=self.camera_resolution)
            self.pose_detection_module.set_camera_input(self.camera_view, camera_view_size=camera_view_size, camera_number=set_camera_number, camera_resolution=self.camera_resolution, settings=self.settings_transition_data.settings)
            self.pose_detection_module.camera_input()
            return True
        else:
            return False


    # Button Actions (Page 0)

    def sensitivity_btn_pressed(self):
        if self.settings_transition_data.settings.sensitivity_level == SENSITIVITY_LEVEL.VERY_HIGH:
            self.settings_transition_data.settings.sensitivity_level = SENSITIVITY_LEVEL.LOW
        elif self.settings_transition_data.settings.sensitivity_level == SENSITIVITY_LEVEL.LOW:
            self.settings_transition_data.settings.sensitivity_level = SENSITIVITY_LEVEL.MEDIUM
        elif self.settings_transition_data.settings.sensitivity_level == SENSITIVITY_LEVEL.MEDIUM:
            self.settings_transition_data.settings.sensitivity_level = SENSITIVITY_LEVEL.HIGH
        elif self.settings_transition_data.settings.sensitivity_level == SENSITIVITY_LEVEL.HIGH:
            self.settings_transition_data.settings.sensitivity_level = SENSITIVITY_LEVEL.VERY_HIGH
        elif self.settings_transition_data.settings.sensitivity_level == SENSITIVITY_LEVEL.VERY_HIGH:
            self.settings_transition_data.settings.sensitivity_level = SENSITIVITY_LEVEL.LOW
        self.gui_update()


    def danger_alert_btn_pressed(self):
        self.settings_transition_data.settings.update(is_danger_alert_on=not self.settings_transition_data.settings.is_danger_alert_on)
        self.gui_update()


    def test_sound_btn_pressed(self):
        SoundModule().test_sound()


    def distance_calibration_btn_pressed(self):
        self.is_distance_calibration_shown = True
        self.gui_update()


    def distance_calibration_up_btn_pressed(self):
        self.settings_transition_data.settings.update(distance_calibration_actual_value=self.settings_transition_data.settings.distance_calibration_actual_value+0.05)
        self.gui_update()


    def distance_calibration_down_btn_pressed(self):
        if self.settings_transition_data.settings.distance_calibration_actual_value > 0.05:
            self.settings_transition_data.settings.update(distance_calibration_actual_value=self.settings_transition_data.settings.distance_calibration_actual_value-0.05)
        self.gui_update()


    def ground_calibration_up_btn_pressed(self):
        if self.settings_transition_data.settings.ground_ratio_calibration_actual_value > 0.01:
            self.settings_transition_data.settings.update(ground_ratio_calibration_actual_value=self.settings_transition_data.settings.ground_ratio_calibration_actual_value-0.025)
        self.gui_update()


    def ground_calibration_down_btn_pressed(self):
        if self.settings_transition_data.settings.ground_ratio_calibration_actual_value < 1:
            self.settings_transition_data.settings.update(ground_ratio_calibration_actual_value=self.settings_transition_data.settings.ground_ratio_calibration_actual_value+0.025)
        self.gui_update()


    def distance_calibration_confirm_btn_pressed(self):
        self.is_distance_calibration_shown = False
        self.gui_update()


    def set_game_path_btn_pressed(self):
        self.navigate(SCREEN.PATHS, camera_mode=CAMERA_MODE.SETTINGS, settings_transition_data=self.settings_transition_data)


    # Button Actions (Page 1)

    def change_camera_btn_pressed(self):
        if not self.is_camera_detected:
            self.is_camera_detected = self.restart_camera(0)
            if self.is_camera_detected:
                self.settings_transition_data.settings.update(camera_number=0)
            else:
                # Fail to restart camera (not detected)
                ctypes.windll.user32.MessageBoxW(0, i18n.t('t.no_camera_is_detected'), i18n.t('t.camera_is_unavailable'), 0)
        else: 
            self.is_camera_detected = self.restart_camera(self.settings_transition_data.settings.camera_number+1)
            if self.is_camera_detected:
                self.settings_transition_data.settings.update(camera_number=self.settings_transition_data.settings.camera_number+1)
            else:
                self.is_camera_detected = self.restart_camera(0)
                if self.is_camera_detected:
                    self.settings_transition_data.settings.update(camera_number=0)
                else:
                    # Fail to restart camera (not detected)
                    ctypes.windll.user32.MessageBoxW(0, i18n.t('t.no_camera_is_detected'), i18n.t('t.camera_is_unavailable'), 0)
        self.gui_update()


    def camera_orientation_btn_pressed(self):
        if self.settings_transition_data.settings.camera_orientation_mode == CAMERA_ORIENTATION.LANDSCAPE:
            self.settings_transition_data.settings.update(camera_orientation_mode=CAMERA_ORIENTATION.LEFT)
        elif self.settings_transition_data.settings.camera_orientation_mode == CAMERA_ORIENTATION.LEFT:
            self.settings_transition_data.settings.update(camera_orientation_mode=CAMERA_ORIENTATION.INVERTED)
        elif self.settings_transition_data.settings.camera_orientation_mode == CAMERA_ORIENTATION.INVERTED:
            self.settings_transition_data.settings.update(camera_orientation_mode=CAMERA_ORIENTATION.RIGHT)
        elif self.settings_transition_data.settings.camera_orientation_mode == CAMERA_ORIENTATION.RIGHT:
            self.settings_transition_data.settings.update(camera_orientation_mode=CAMERA_ORIENTATION.LANDSCAPE)
        self.gui_camera_view_rotate()
        self.gui_update()


    def mirror_camera_btn_pressed(self):
        self.settings_transition_data.settings.update(is_mirror_camera=not self.settings_transition_data.settings.is_mirror_camera)
        self.gui_update()

    
    def reverse_keypad_btn_pressed(self):
        self.settings_transition_data.settings.update(is_keypad_reverse=not self.settings_transition_data.settings.is_keypad_reverse)
        self.change_keypad(self.settings_transition_data.settings.is_keypad_reverse)
        self.gui_update()


    def toggle_page_btn_pressed(self):
        if self.current_page == 0:
            self.current_page = 1
        elif self.current_page == 1:
            self.current_page = 0
        self.gui_update()


    def cancel_btn_pressed(self):
        result = ctypes.windll.user32.MessageBoxW(None, i18n.t('t.confirm_cancel_settings'), i18n.t('t.alert'), 1)
        if result == 1:
            # User pressed ok
            self.save_load_module.save_settings(self.old_settings)
            self.change_keypad(self.old_settings.is_keypad_reverse)
            self.navigate(SCREEN.HOME)


    def confirm_btn_pressed(self):
        result = ctypes.windll.user32.MessageBoxW(None, i18n.t('t.confirm_confirm_settings'), i18n.t('t.alert'), 1)
        if result == 1:
            # User pressed ok
            self.save_load_module.save_settings(self.settings_transition_data.settings)
            self.save_load_module.save_path_data(settings_transition_data=self.settings_transition_data)
            self.change_keypad(self.settings_transition_data.settings.is_keypad_reverse)
            self.navigate(SCREEN.HOME)


    # GUI Methods

    def gui_camera_view_set(self, camera_resolution: Resolution) -> Resolution:
        background_view_ratio = self.background_view_size.width / self.view_size.height
        camera_view_ratio = camera_resolution.width / camera_resolution.height
        if background_view_ratio > camera_view_ratio:
            # The width of background_view is larger than the width of camera_view
            camera_view_height = int(self.view_size.height)
            camera_view_width = int(self.view_size.height * camera_view_ratio)
        else:
            # The height of background_view is larger than the height of camera_view
            camera_view_width = int(self.background_view_size.width)
            camera_view_height = int(self.background_view_size.width / camera_view_ratio)
        self.camera_view.place(x=self.background_view_size.width/2, rely=0.5, height=camera_view_height, width=camera_view_width, anchor=CENTER)
        camera_view_size = Resolution(width=camera_view_width, height=camera_view_height)
        return camera_view_size


    def gui_camera_view_rotate(self):
        if self.is_camera_detected:
            self.camera_resolution = Resolution(width=self.camera_resolution.height, height=self.camera_resolution.width)
            camera_view_size = self.gui_camera_view_set(camera_resolution=self.camera_resolution)
            self.pose_detection_module.update_camera_view(camera_view=self.camera_view, size=camera_view_size)


    def gui_set(self):
        self.background_view.place(width=self.background_view_size.width, relheight=1.0)
        self.label_view.place(x=self.background_view_size.width, width=self.view_size.width-self.background_view_size.width, relheight=1.0)


    def gui_update(self):
        self.gui_clear()

        self.pose_detection_module.update_settings(self.settings_transition_data.settings, is_distance_calibration_shown=self.is_distance_calibration_shown)

        if not self.is_camera_detected:

            self.camera_view.place_forget()
            self.background_view.config(text=i18n.t('t.no_camera_is_detected'))
            self.camera_number_label.place_forget()
            self.buttons[0] = ControlBarButton(i18n.t('t.detect_camera'), self.change_camera_btn_pressed)
            self.buttons[1] = ControlBarButton(i18n.t('t.test_sound'), self.test_sound_btn_pressed)
            self.buttons[8] = ControlBarButton(i18n.t('t.cancel'), self.cancel_btn_pressed, THEME_COLOR_PINK)
            self.buttons[9] = ControlBarButton(i18n.t('t.confirm'), self.confirm_btn_pressed, THEME_COLOR_PURPLE)

        elif self.is_distance_calibration_shown:

            actual_value_string = "{:.2f}".format(self.settings_transition_data.settings.distance_calibration_actual_value)
            self.distance_calibration_actual_value_label.config(text=f"""{i18n.t('t.actual_distance_of_the_yellow_line')} {actual_value_string} {i18n.t('t.metre')}""")
            self.ground_calibration_actual_position_label.config(text=i18n.t('t.actual_ground_level'))
            self.distance_calibration_actual_value_label.place(relx=0.5, height=CONTROL_BAR_BUTTON_HEIGHT*2, anchor=N)
            self.ground_calibration_actual_position_label.place(relx=0.5, y=CONTROL_BAR_BUTTON_HEIGHT*2, height=CONTROL_BAR_BUTTON_HEIGHT*2, anchor=N)
            self.buttons[0] = ControlBarButton("↑", self.distance_calibration_up_btn_pressed)
            self.buttons[1] = ControlBarButton("↓", self.distance_calibration_down_btn_pressed)
            self.buttons[2] = ControlBarButton("↑", self.ground_calibration_up_btn_pressed)
            self.buttons[3] = ControlBarButton("↓", self.ground_calibration_down_btn_pressed)
            self.buttons[9] = ControlBarButton(i18n.t('t.confirm'), self.distance_calibration_confirm_btn_pressed, THEME_COLOR_PURPLE)

        else:

            if self.current_page == 0:

                self.sensitivity_label.config(text=i18n.t('t.sensitivity'))
                self.sensitivity_label.place(relx=0.5, height=CONTROL_BAR_BUTTON_HEIGHT, anchor=N)
                if self.settings_transition_data.settings.sensitivity_level == SENSITIVITY_LEVEL.VERY_LOW:
                    self.buttons[0] = ControlBarButton(i18n.t('t.very_low'), self.sensitivity_btn_pressed)
                elif self.settings_transition_data.settings.sensitivity_level == SENSITIVITY_LEVEL.LOW:
                    self.buttons[0] = ControlBarButton(i18n.t('t.low'), self.sensitivity_btn_pressed)
                elif self.settings_transition_data.settings.sensitivity_level == SENSITIVITY_LEVEL.MEDIUM:
                    self.buttons[0] = ControlBarButton(i18n.t('t.medium'), self.sensitivity_btn_pressed)
                elif self.settings_transition_data.settings.sensitivity_level == SENSITIVITY_LEVEL.HIGH:
                    self.buttons[0] = ControlBarButton(i18n.t('t.high'), self.sensitivity_btn_pressed)
                elif self.settings_transition_data.settings.sensitivity_level == SENSITIVITY_LEVEL.VERY_HIGH:
                    self.buttons[0] = ControlBarButton(i18n.t('t.very_high'), self.sensitivity_btn_pressed)

                self.danger_alert_label.config(text=f"{i18n.t('t.danger_alert')}")
                self.danger_alert_label.place(relx=0.5, y=CONTROL_BAR_BUTTON_HEIGHT, height=CONTROL_BAR_BUTTON_HEIGHT, anchor=N)
                if self.settings_transition_data.settings.is_danger_alert_on:
                    self.buttons[1] = ControlBarButton(i18n.t('t.yes'), self.danger_alert_btn_pressed)
                else:
                    self.buttons[1] = ControlBarButton(i18n.t('t.no'), self.danger_alert_btn_pressed)

                self.buttons[2] = ControlBarButton(i18n.t('t.test_sound'), self.test_sound_btn_pressed)
                self.buttons[3] = ControlBarButton(i18n.t('t.distance_calibration'), self.distance_calibration_btn_pressed)
                self.buttons[4] = ControlBarButton(i18n.t('t.set_game_path'), self.set_game_path_btn_pressed)
                self.buttons[7] = ControlBarButton(i18n.t('t.next_page'), self.toggle_page_btn_pressed)

            elif self.current_page == 1:

                self.camera_number_label.config(text=f"{i18n.t('t.camera_number')}: {self.settings_transition_data.settings.camera_number}")
                self.camera_number_label.place(relx=0.5, height=CONTROL_BAR_BUTTON_HEIGHT, anchor=N)
                self.buttons[0] = ControlBarButton(i18n.t('t.change_camera'), self.change_camera_btn_pressed)

                self.camera_orientation_label.config(text=f"{i18n.t('t.camera_orientation')}")
                self.camera_orientation_label.place(relx=0.5, y=CONTROL_BAR_BUTTON_HEIGHT, height=CONTROL_BAR_BUTTON_HEIGHT, anchor=N)
                if self.settings_transition_data.settings.camera_orientation_mode == CAMERA_ORIENTATION.LANDSCAPE:
                    self.buttons[1] = ControlBarButton(i18n.t('t.landscape'), self.camera_orientation_btn_pressed)
                elif self.settings_transition_data.settings.camera_orientation_mode == CAMERA_ORIENTATION.LEFT:
                    self.buttons[1] = ControlBarButton(i18n.t('t.left'), self.camera_orientation_btn_pressed)
                elif self.settings_transition_data.settings.camera_orientation_mode == CAMERA_ORIENTATION.INVERTED:
                    self.buttons[1] = ControlBarButton(i18n.t('t.inverted'), self.camera_orientation_btn_pressed)
                elif self.settings_transition_data.settings.camera_orientation_mode == CAMERA_ORIENTATION.RIGHT:
                    self.buttons[1] = ControlBarButton(i18n.t('t.right'), self.camera_orientation_btn_pressed)
                
                self.camera_mirror_label.config(text=f"{i18n.t('t.mirror_camera')}")
                self.camera_mirror_label.place(relx=0.5, y=CONTROL_BAR_BUTTON_HEIGHT*2, height=CONTROL_BAR_BUTTON_HEIGHT, anchor=N)
                if self.settings_transition_data.settings.is_mirror_camera:
                    self.buttons[2] = ControlBarButton(i18n.t('t.yes'), self.mirror_camera_btn_pressed)
                else:
                    self.buttons[2] = ControlBarButton(i18n.t('t.no'), self.mirror_camera_btn_pressed)

                self.reverse_keypad_label.config(text=f"{i18n.t('t.reverse_keypad')}")
                self.reverse_keypad_label.place(relx=0.5, y=CONTROL_BAR_BUTTON_HEIGHT*3, height=CONTROL_BAR_BUTTON_HEIGHT, anchor=N)
                if self.settings_transition_data.settings.is_keypad_reverse:
                    self.buttons[3] = ControlBarButton(i18n.t('t.yes'), self.reverse_keypad_btn_pressed)
                else:
                    self.buttons[3] = ControlBarButton(i18n.t('t.no'), self.reverse_keypad_btn_pressed)

                self.buttons[7] = ControlBarButton(i18n.t('t.previous_page'), self.toggle_page_btn_pressed)

            self.buttons[8] = ControlBarButton(i18n.t('t.cancel'), self.cancel_btn_pressed, THEME_COLOR_PINK)
            self.buttons[9] = ControlBarButton(i18n.t('t.confirm'), self.confirm_btn_pressed, THEME_COLOR_PURPLE)

        self.change_title(i18n.t('t.settings'))
        self.change_buttons(self.buttons)


    def gui_clear(self):
        self.background_view.config(text='')
        self.sensitivity_label.place_forget()
        self.danger_alert_label.place_forget()
        self.distance_calibration_actual_value_label.place_forget()
        self.ground_calibration_actual_position_label.place_forget()
        self.camera_number_label.place_forget()
        self.camera_orientation_label.place_forget()
        self.camera_mirror_label.place_forget()
        self.reverse_keypad_label.place_forget()
        self.buttons = {}