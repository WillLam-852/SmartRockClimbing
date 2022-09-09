import i18n
import ctypes
# import tkinter.messagebox
# from typing import List
from tkinter import *
from Models.Camera.Resolution import Resolution
from Models.Enums.CameraOrientation import CAMERA_ORIENTATION
from Models.Enums.CameraState import CAMERA_STATE
from Models.Point import Point
# from tkinter.simpledialog import askstring

from Models.SavedData import SavedData, SavedPath, SavedPoint
from Models.Enums.Screen import SCREEN
from Models.Enums.CameraMode import CAMERA_MODE
# from Models.Enums.CameraState import CAMERA_STATE
# from Models.Enums.GameMode import GAME_MODE
# from Widgets.ControlBarButton import ControlBarButton
# # from Models.Timer import Timer
from Modules.SaveLoadModule import SaveLoadModule
from Modules.PoseDetectionModule import PoseDetectionModule
from Utilities.Constants import *
from Widgets.ControlBarButton import ControlBarButton

class CameraScreen(Frame):

    def __init__(self, *arg, view_size: Resolution, navigate, change_title, change_buttons, **kwargs):
        Frame.__init__(self, *arg, **kwargs)
        
        self.view_size = view_size

        self.navigate_without_stop_camera = navigate
        self.change_title = change_title
        self.change_buttons = change_buttons

        self.background_view = Label(self, bg='black')
        self.camera_view = Label(self)

#         if DEBUG_MODE:
#             self.camera_view.bind("<B1-Motion>", self.screen_moved)

        self.camera_view.bind("<ButtonRelease-1>", self.screen_pressed_left)
#         self.camera_view.bind("<ButtonRelease-3>", self.screen_pressed_right)

        self.distance_angle_label = Label(self, font=(FONT_FAMILY, TITLE_FONT_SIZE), bg=THEME_COLOR)
        self.status_label = Label(self, font=(FONT_FAMILY, TITLE_FONT_SIZE), bg=THEME_COLOR)
        # self.countdown_label = Label(self, font=(FONT_FAMILY, COUNTDOWN_FONT_SIZE), borderwidth=5, relief='solid', bg=THEME_COLOR)
        # self.timer_label = Label(self, font=(FONT_FAMILY, TITLE_FONT_SIZE), bg=THEME_COLOR)
        # self.progress_label = Label(self, font=(FONT_FAMILY, TITLE_FONT_SIZE), bg=THEME_COLOR)
        self.reminder_label = Label(self, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE), bg=THEME_COLOR)

        self.gui_set()

#         # self.point_sequence = 0
#         # self.alphabet = ''

#         # self.countdown = None
#         # self.timer = None
        self.save_load_module = SaveLoadModule()
        self.pose_detection_module = PoseDetectionModule()


#     # Navigation Methods

    def launch(self, camera_mode=CAMERA_MODE.NORMAL, path:SavedPath=None, points:list[SavedPoint]=[]):
        i18n.set('locale', self.save_load_module.load_locale())
        self.change_title(i18n.t('t.camera'))
        self.camera_mode = camera_mode
        settings = self.save_load_module.load_settings()
        camera_number = settings.camera_number

        # Test camera with camera number stored in settings
        camera_resolution = self.pose_detection_module.get_camera_resolution(camera_number)
        if camera_resolution is None:
            # Update camera number == 0
            camera_number = 0
            settings.update(camera_number=camera_number)
            self.save_load_module.save_settings(settings)
            # Test camera with camera number == 0
            camera_resolution = self.pose_detection_module.get_camera_resolution(camera_number)
            if camera_resolution is None:
                # If there is still no camera detected, go back to home view
                ctypes.windll.user32.MessageBoxW(0, i18n.t('t.no_camera_is_detected'), i18n.t('t.camera_is_unavailable'), 0)
                self.navigate(SCREEN.HOME)
                return

        if settings.camera_orientation_mode == CAMERA_ORIENTATION.LEFT or settings.camera_orientation_mode == CAMERA_ORIENTATION.RIGHT:
            camera_resolution.exchange_width_height()

        camera_view_size = self.gui_camera_view_set(camera_resolution=camera_resolution)
        self.pose_detection_module.set_camera_input(self.camera_view, camera_view_size=camera_view_size, camera_number=camera_number, camera_resolution=camera_resolution, settings=settings)
        self.pose_detection_module.cameraInput()

        self.gui_buttons_set()
        self.change_camera_state(CAMERA_STATE.PLAYING)


#         self.game_mode = game_mode
#         self.path_id = path_id
#         self.path_name = path_name
#         self.path_data: List[SavedData] = saved_file
#         self.path_images = path_images

#         if self.camera_mode == CAMERA_MODE.GAME or self.camera_mode == CAMERA_MODE.SETTINGS:
#             points_copy = []
#             for point in path_points:
#                 points_copy.append((point[0], point[1], point[2], point[3], point[4]))
            
#             self.path_name = str(path_name)
#             self.change_title(self.path_name)

#             if self.camera_mode == CAMERA_MODE.GAME:
#                 self.good_points_is_shown = True
#                 if self.game_mode == GAME_MODE.OBSTACLE:
#                     self.bad_points_is_shown = True
#                 else:
#                     self.bad_points_is_shown = False
#                 self.pose_detection.game_start(path_id, points_copy, self.game_mode, progress_callback=self.progress_update)
#                 self.pose_detection.game_toggle_show_good_points(is_shown=self.good_points_is_shown)
#                 self.pose_detection.game_toggle_show_bad_points(is_shown=self.bad_points_is_shown)

#             if self.camera_mode == CAMERA_MODE.SETTINGS:
#                 self.pose_detection.settings_start(path_id, points_copy, gamemode=self.game_mode)

#         self.clear_labels()


    
    def navigate(self, view, **kwargs):
        self.pose_detection_module.stop_camera_input()
        # if self.countdown is not None:
        #     self.countdown.reset()
        # if self.timer is not None:
        #     self.timer.reset()
        self.navigate_without_stop_camera(view, **kwargs)


    # Camera Methods

    def change_camera_state(self, state):
        self.clear_camera_state()
        if self.camera_mode == CAMERA_MODE.NORMAL:
            if state == CAMERA_STATE.PLAYING:
                self.buttons[0] = ControlBarButton(i18n.t('t.pause'), lambda: self.change_camera_state(CAMERA_STATE.PAUSE))
                self.buttons[1] = ControlBarButton(i18n.t('t.record'), lambda: self.change_camera_state(CAMERA_STATE.RECORDING))
            elif state == CAMERA_STATE.PAUSE:
                self.status_label.config(text=f"{i18n.t('t.pause')}...")
                self.status_label.place(x=15, y=15)
                self.buttons[0] = ControlBarButton(i18n.t('t.play'), lambda: self.change_camera_state(CAMERA_STATE.PLAYING))
                self.buttons[1] = ControlBarButton(i18n.t('t.clear'), lambda: self.clear_btn_pressed())
            elif state == CAMERA_STATE.RECORDING:
                self.status_label.config(text=f"{i18n.t('t.recording')}...")
                self.status_label.place(x=15, y=15)
                self.buttons[1] = ControlBarButton(i18n.t('t.stop_recording'), lambda: self.change_camera_state(CAMERA_STATE.PLAYING))

        # elif self.camera_mode == CAMERA_MODE.GAME:
        #     if state == CAMERA_STATE.PLAYING:
        #         self.buttons[5] = ControlBarButton(i18n.t('t.record'), lambda: self.change_camera_state(CAMERA_STATE.RECORDING))
        #     elif state == CAMERA_STATE.RECORDING:
        #         self.status_label.config(text=f"{i18n.t('t.recording')}...")
        #         self.status_label.place(x=15, y=15)
        #         self.buttons[5] = ControlBarButton(i18n.t('t.stop_recording'), lambda: self.change_camera_state(CAMERA_STATE.PLAYING))

        self.pose_detection_module.change_camera_state(state)
        self.camera_state = state
        self.change_buttons(self.buttons)


    def clear_camera_state(self):
        if self.camera_mode == CAMERA_MODE.NORMAL:
            self.buttons.pop(0, None)
            self.buttons.pop(1, None)
        if self.camera_mode == CAMERA_MODE.GAME:
            self.buttons.pop(5, None)
        self.status_label.place_forget()
        self.distance_angle_label.place_forget()


#     def change_game_mode_btn_pressed(self):
#         self.clear_all_touch_points_btn_pressed()
#         self.clear_all_avoid_points_btn_pressed()
#         self.pose_detection.game_change_game_mode(self.game_mode)
#         self.alphabet = ''
#         if self.game_mode == GAME_MODE.OBSTACLE:
#             self.change_title(self.path_name)
#             self.game_mode = GAME_MODE.SEQUENCE
#         elif self.game_mode == GAME_MODE.SEQUENCE:
#             self.change_title(self.path_name + ' (' + i18n.t('t.game_mode_2') + ') ')
#             self.game_mode = GAME_MODE.ALPHABET
#         elif self.game_mode == GAME_MODE.ALPHABET:
#             self.change_title(self.path_name + ' (' + i18n.t('t.game_mode_0') + ') ')
#             self.game_mode = GAME_MODE.OBSTACLE


#     # Timer Methods

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


#     # Finish Game Mode

#     def progress_update(self, touched, all):
#         if self.game_mode == GAME_MODE.OBSTACLE or self.game_mode == GAME_MODE.SEQUENCE:
#             self.progress_label.config(text=f"{touched}/{all}")
#             if touched == all:
#                 self.finish_btn_pressed()
#         elif self.game_mode == GAME_MODE.ALPHABET:
#             self.progress_label.config(text=f"{touched}")


#     # Button Actions

    def clear_btn_pressed(self):
        self.pose_detection_module.clear_all_dots()
        self.distance_angle_label.place_forget()


    def screen_pressed_left(self, event):
        point = Point(x=event.x, y=event.y)
        if self.camera_mode == CAMERA_MODE.NORMAL or self.camera_mode == CAMERA_MODE.GAME:
            if self.camera_state == CAMERA_STATE.PAUSE:
                calculationResult = self.pose_detection_module.tap_on_screen(point)
                if calculationResult.distance:
                    self.distance_angle_label.config(text=i18n.t('t.distance')+": {:.2f} m".format(calculationResult.distance))
                    self.distance_angle_label.place(relx=0.5, y=15, anchor=N)                
                elif calculationResult.angle:
                    self.distance_angle_label.config(text=i18n.t('t.angle')+":{:.2f}".format(calculationResult.angle))
                    self.distance_angle_label.place(relx=0.5, y=15, anchor=N)
                else:
                    self.distance_angle_label.place_forget()
#         elif self.camera_mode == CAMERA_MODE.SETTINGS:
#             if self.game_mode == GAME_MODE.ALPHABET:
#                 self.alphabet = askstring('Alphabet', 'Please input alphabet')
#             else:
#                 self.alphabet = ''
#             self.pose_detection.settings_game_screen_pressed(point=(event.x, event.y), is_good=True, point_squence=self.point_sequence, alphabet=self.alphabet, gamemode=self.game_mode)
#             if self.game_mode == GAME_MODE.SEQUENCE or self.game_mode == GAME_MODE.ALPHABET:
#                 self.point_sequence += 1
#             else:
#                 self.point_sequence = 0
#         if DEBUG_MODE:
#             self.pose_detection.simulate_body_point()


#     def screen_pressed_right(self, event):
#         if self.camera_mode == CAMERA_MODE.SETTINGS and self.game_mode == GAME_MODE.OBSTACLE:
#             self.pose_detection.settings_game_screen_pressed(point=(event.x, event.y), is_good=False, point_squence=0, alphabet=self.alphabet, gamemode=self.game_mode)


#     # Button Actions (Game)

#     def finish_btn_pressed(self):
#         result = self.pose_detection.game_finish()
#         result.update_time(self.timer_label['text'])
#         self.pose_detection.stop_camera_input()
#         self.navigate(VIEW.RESULT, result=result, gamemode=self.game_mode)


#     def return_btn_pressed(self):
#         self.pose_detection.stop_camera_input()
#         self.navigate(VIEW.PATHS)


#     def good_points_button_pressed(self):
#         self.good_points_is_shown = not self.good_points_is_shown
#         self.pose_detection.game_toggle_show_good_points(is_shown=self.good_points_is_shown)
#         self.reset_toggle_buttons()


#     def bad_points_button_pressed(self):
#         self.bad_points_is_shown = not self.bad_points_is_shown
#         self.pose_detection.game_toggle_show_bad_points(is_shown=self.bad_points_is_shown)
#         self.reset_toggle_buttons()


#     def reset_toggle_buttons(self):
#         if self.good_points_is_shown:
#             self.buttons[2] = ControlBarButton(f"{i18n.t('t.hide_touch_points')}", self.good_points_button_pressed)
#         else:
#             self.buttons[2] = ControlBarButton(f"{i18n.t('t.show_touch_points')}", self.good_points_button_pressed)
#         if self.bad_points_is_shown:
#             self.buttons[3] = ControlBarButton(f"{i18n.t('t.hide_avoid_points')}", self.bad_points_button_pressed)
#         else:
#             self.buttons[3] = ControlBarButton(f"{i18n.t('t.show_avoid_points')}", self.bad_points_button_pressed)
#         self.change_buttons(self.buttons)


#     # Button Actions (Settings)

#     def undo_btn_pressed(self):
#         self.pose_detection.settings_path_undo()


#     def redo_btn_pressed(self):
#         self.pose_detection.settings_path_redo()


#     def clear_all_points_btn_pressed(self):
#         self.point_sequence = 0
#         self.pose_detection.settings_path_clear_all_points()


#     def cancel_btn_pressed(self):
#         self.navigate(VIEW.PATHS, is_settings=True, path_data=self.path_data)


#     def confirm_btn_pressed(self):
#         have_good_points = False
#         new_points, new_image = self.pose_detection.settings_path_done()
#         # Check if there is any good points
#         for point in new_points:
#             if point.is_good:
#                 have_good_points = True
#         if have_good_points:
#             new_path_data: List[SavedData] = self.path_data.copy()
#             # Remove all points of this path
#             for row in self.path_data:
#                 if row.path_id == self.path_id:
#                     new_path_data.remove(row)
            
#             self.path_images.append((self.path_id, new_image))
#             for point in new_points:
#                 new_row = SavedData(path_id=self.path_id, path_name=self.path_name, path_gamemode=self.game_mode, point_x=)
#                 new_path_data.append([self.path_id, self.path_name, point[0], point[1], point[2], point[3], point[4], self.game_mode.value])
#             self.navigate(VIEW.PATHS, is_settings=True, path_data=new_path_data, path_images=self.path_images)
#         else:
#             # If no good point, show error message
#             tkinter.messagebox.showerror(title=i18n.t('t.error'), message=i18n.t('t.error_path'))


#     # Other Methods

#     def clear_labels(self):
#         self.countdown_label.place_forget()
#         self.reminder_label.place_forget()
#         self.timer_label.place_forget()
#         self.progress_label.place_forget()


#     def show_danger_alerts(self, show):
#         if show:
#             self.reminder_label.place(relx=0.5, rely=1.0, y=-10, width=600, anchor=S)
#         else:
#             self.reminder_label.place_forget()


#     # GUI Methods

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
        camera_view_size = Resolution(width=camera_view_width, height=camera_view_height)
        self.camera_view.place(relx=0.5, rely=0.5, width=camera_view_width, height=camera_view_height, anchor=CENTER)
        return camera_view_size


    def gui_buttons_set(self):
        if self.camera_mode == CAMERA_MODE.GAME:
            pass
#             self.buttons = {
#                 0: ControlBarButton(i18n.t('t.finish'), self.finish_btn_pressed),
#                 2: ControlBarButton(i18n.t('t.hide_touch_points'), self.good_points_button_pressed),
#                 3: ControlBarButton(i18n.t('t.hide_avoid_points'), self.bad_points_button_pressed),
#                 5: ControlBarButton(i18n.t('t.record'), lambda: self.change_camera_state(CAMERA_STATE.RECORDING)),
#                 9: ControlBarButton(i18n.t('t.leave'), lambda: self.navigate(VIEW.PATHS), THEME_COLOR_PINK)
#             }
#             self.countdown = Timer(self.countdown_update, True, 6, self.countdown_finish)
#             self.countdown.start()
#             self.countdown_label.place(relx=0.5, rely=0.5, width=400, height=400, anchor=CENTER)
#             self.reminder_label.config(text=f"{i18n.t('t.DANGER_ALERT_Two_hands_are_outside_feet_area')}")

#             # A new window is created in a separate monitor for projector to project on the surface of rock climbing wall
#             # projector_view = Toplevel(self)
#             # projector_view.overrideredirect(True)
#             # projector_view.geometry('%dx%d+%d+%d'%(1920,1080,0,-1080))
#             # projector_view.attributes('-fullscreen', False)
#             # projector_view.title("New Window")
#             # print(WINDOW_HEIGHT, WINDOW_WIDTH)
#             # projector_view.pose_detection.cameraInput()


#         elif self.camera_mode == CAMERA_MODE.SETTINGS:
#             self.buttons = {
#                 0: ControlBarButton(i18n.t('t.change_game_mode'), self.change_game_mode_btn_pressed),
#                 2: ControlBarButton(i18n.t('t.undo'), self.undo_btn_pressed),
#                 3: ControlBarButton(i18n.t('t.redo'), self.redo_btn_pressed),
#                 4: ControlBarButton(i18n.t('t.clear_all_points'), self.clear_all_points_btn_pressed),
#                 8: ControlBarButton(i18n.t('t.cancel'), self.cancel_btn_pressed, THEME_COLOR_PINK),
#                 9: ControlBarButton(i18n.t('t.confirm'), self.confirm_btn_pressed, THEME_COLOR_PURPLE)
#             }
#             self.reminder_label.config(text=f"""{i18n.t('t.press_left_mouse_button_for_new_touch_point')}
# {i18n.t('t.press_right_mouse_button_for_new_avoid_point')}""")
#             self.reminder_label.place(relx=0.5, rely=1.0, y=-10, width=600, anchor=S)
#             self.point_sequence = 0
#             self.alphabet = ''

        else:
            self.buttons = {
                0: ControlBarButton(i18n.t('t.pause'), lambda: self.change_camera_state(CAMERA_STATE.PAUSE)),
                1: ControlBarButton(i18n.t('t.record'), lambda: self.change_camera_state(CAMERA_STATE.RECORDING)),
                9: ControlBarButton(i18n.t('t.home'), lambda: self.navigate(SCREEN.HOME), THEME_COLOR_PINK)
            }
            self.reminder_label.config(text=f"{i18n.t('t.DANGER_ALERT_Two_hands_are_outside_feet_area')}")

        self.change_buttons(self.buttons)
        

    def gui_set(self):
        self.background_view.place(relwidth=1.0, relheight=1.0)


#     # Debug Methods

#     def screen_moved(self, event):
#         self.pose_detection.simulate_body_point((event.x, event.y))