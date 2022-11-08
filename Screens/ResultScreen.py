import PIL
import cv2
import i18n
import numpy as np
from tkinter import *

from Models.Enums.CameraOrientation import CAMERA_ORIENTATION
from Models.Enums.GameMode import GAME_MODE
from Models.Enums.Screen import SCREEN
from Models.Path.GameResult import GameResult
from Models.Path.Path import Path
from Models.Resolution import Resolution
from Modules.PoseDetectionModule import PoseDetectionModule
from Modules.SaveLoadModule import SaveLoadModule
from Utilities.Constants import *
from Widgets.ControlBarButton import ControlBarButton

class ResultScreen(Frame):

    def __init__(self, *arg, view_size: Resolution, navigate, change_title, change_buttons, **kwargs):
        Frame.__init__(self, *arg, **kwargs)
        
        self.view_size = view_size
        self.navigate = navigate
        self.change_title = change_title
        self.change_buttons = change_buttons
        
        self.timer_label = Label(self, font=(FONT_FAMILY, HEADING_FONT_SIZE), fg="black", bg=THEME_COLOR_BLUE)
        self.good_points_label = Label(self, font=(FONT_FAMILY, HEADING_FONT_SIZE), fg="black", relief=RIDGE, bg=THEME_COLOR_BLUE)
        self.bad_points_label = Label(self, font=(FONT_FAMILY, HEADING_FONT_SIZE), fg="black", relief=RIDGE, bg=THEME_COLOR_BLUE)
        self.score_label = Label(self, font=(FONT_FAMILY, TITLE_FONT_SIZE), fg="black", relief=RIDGE, bg=THEME_COLOR_BLUE)
        self.full_score_label = Label(self, font=(FONT_FAMILY, HEADING_FONT_SIZE), fg="black", relief=RIDGE, bg=THEME_COLOR_BLUE)

        self.result_image_view = Label(self)

        self.gui_set()


    # Navigation Methods

    def launch(self, path: Path, game_result: GameResult):
        """
        Parameters
        ----------
        path : Path
            current path
        game_result : GameResult
            current game result
        """
        self.settings = SaveLoadModule().load_settings()
        i18n.set('locale', SaveLoadModule().load_locale())
        self.change_title(i18n.t('t.result'))
        self.buttons = {
            0: ControlBarButton(i18n.t('t.view_image'), self.view_image_btn_pressed),
            9: ControlBarButton(i18n.t('t.home'), lambda: self.navigate(SCREEN.HOME), THEME_COLOR_PINK)
        }
        self.change_buttons(self.buttons)

        self.game_result: GameResult = game_result
        self.path: Path = path
        self.show()


    def show(self):
        time = self.game_result.get_time()
        self.timer_label.config(text=f"{i18n.t('t.time')}: {time}")

        if self.path.game_mode == GAME_MODE.OBSTACLE:
            touched_good_points_number, total_good_points_number = self.game_result.get_good_points_number()
            add_scores: int = touched_good_points_number * TOUCHED_GOOD_POINT_WEIGHT
            self.good_points_label.config(
                text=f'''{i18n.t('t.touch_points')}: {touched_good_points_number} / {total_good_points_number}
{i18n.t('t.scores_get')}:   {TOUCHED_GOOD_POINT_WEIGHT} x {touched_good_points_number} = {add_scores}''')

            touched_bad_points_number, total_bad_points_number = self.game_result.get_bad_points_number()
            minus_scores: int = touched_bad_points_number * TOUCHED_BAD_POINT_WEIGHT
            self.bad_points_label.config(
                text=f'''{i18n.t('t.avoid_points')}: {touched_bad_points_number} / {total_bad_points_number}
{i18n.t('t.scores_deducted')}: {TOUCHED_BAD_POINT_WEIGHT} x {touched_bad_points_number} = {minus_scores}''')

            score = self.game_result.get_score()
            full_score = self.game_result.get_full_score()
            self.score_label.config(text=f"{i18n.t('t.total_score')}: {score}")
            self.full_score_label.config(text=f"{i18n.t('t.full_score')}: {full_score}")

        elif self.path.game_mode == GAME_MODE.SEQUENCE:
            touched_good_points_number, total_good_points_number = self.game_result.get_good_points_number()
            add_scores: int = touched_good_points_number * TOUCHED_GOOD_POINT_WEIGHT
            self.good_points_label.config(
                text=f'''{i18n.t('t.touch_points')}: {touched_good_points_number} / {total_good_points_number}
{i18n.t('t.scores_get')}:   {TOUCHED_GOOD_POINT_WEIGHT} x {touched_good_points_number} = {add_scores}''')

            score = self.game_result.get_score()
            full_score = self.game_result.get_full_score()
            self.score_label.config(text=f"{i18n.t('t.total_score')}: {score}")
            self.full_score_label.config(text=f"{i18n.t('t.full_score')}: {full_score}")

        elif self.path.game_mode == GAME_MODE.ALPHABET:
            self.good_points_label.config(text=f"The word you have spelt is:")
            self.bad_points_label.config(text=f"{self.game_result.get_word()}")
            self.score_label.config(text="")
            self.full_score_label.config(text="")


    # Button Actions

    def view_image_btn_pressed(self):
        numpy_img = self.game_result.get_image()
        touched_good_points, untouched_good_points, touched_bad_points, untouched_bad_points = self.game_result.get_points_lists()

        if self.settings.is_mirror_camera:
            numpy_img = cv2.flip(numpy_img, 1)
        if self.settings.camera_orientation_mode == CAMERA_ORIENTATION.LEFT:
            numpy_img = cv2.rotate(numpy_img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif self.settings.camera_orientation_mode == CAMERA_ORIENTATION.RIGHT:
            numpy_img = cv2.rotate(numpy_img, cv2.ROTATE_90_CLOCKWISE)
        elif self.settings.camera_orientation_mode == CAMERA_ORIENTATION.INVERTED:
            numpy_img = cv2.rotate(numpy_img, cv2.ROTATE_180)

        pose_detection_module = PoseDetectionModule()
        pose_detection_module.settings_update_settings(settings=self.settings)
        image_resolution = Resolution(width=numpy_img.shape[1], height=numpy_img.shape[0])
        image_view_size = self.gui_image_view_calculate(image_resolution=image_resolution)
        pose_detection_module.update_camera_view(camera_view=self.result_image_view, size=image_view_size)
        numpy_img = cv2.resize(numpy_img, (image_view_size.width, image_view_size.height))

        for point in touched_good_points:
            camera_point = pose_detection_module.map_to_camera_point(point)
            cv2.circle(numpy_img, (int(camera_point.x), int(camera_point.y)), DOT_RADIUS, TOUCHED_GOOD_POINTS_COLOR, -1)
        for point in untouched_good_points:
            camera_point = pose_detection_module.map_to_camera_point(point)
            cv2.circle(numpy_img, (int(camera_point.x), int(camera_point.y)), DOT_RADIUS, GOOD_POINTS_COLOR, -1)
        for point in touched_bad_points:
            camera_point = pose_detection_module.map_to_camera_point(point)
            cv2.circle(numpy_img, (int(camera_point.x), int(camera_point.y)), DOT_RADIUS, TOUCHED_BAD_POINTS_COLOR, -1)
        for point in untouched_bad_points:
            camera_point = pose_detection_module.map_to_camera_point(point)
            cv2.circle(numpy_img, (int(camera_point.x), int(camera_point.y)), DOT_RADIUS, BAD_POINTS_COLOR, -1)
        
        self.img = PIL.ImageTk.PhotoImage(PIL.Image.fromarray(np.uint8(numpy_img)))
        self.result_image_view.config(image=self.img)
        self.result_image_view.place(relx=0.5, rely=0.5, width=image_view_size.width, height=image_view_size.height, anchor=CENTER)
        self.timer_label.place_forget()
        self.good_points_label.place_forget()
        self.bad_points_label.place_forget()
        self.score_label.place_forget()
        self.full_score_label.place_forget()
        self.buttons = {
            0: ControlBarButton(i18n.t('t.return'), self.return_btn_pressed)
        }
        self.change_buttons(self.buttons)


    def return_btn_pressed(self):
        self.result_image_view.place_forget()
        self.gui_set()
        self.buttons = {
            0: ControlBarButton(i18n.t('t.view_image'), self.view_image_btn_pressed),
            9: ControlBarButton(i18n.t('t.home'), lambda: self.navigate(SCREEN.HOME), THEME_COLOR_PINK)
        }
        self.change_buttons(self.buttons)


    # GUI Methods

    def gui_image_view_calculate(self, image_resolution: Resolution) -> Resolution:
        background_view_ratio = self.view_size.width / self.view_size.height
        image_view_ratio = image_resolution.width / image_resolution.height
        if background_view_ratio > image_view_ratio:
            # The width of background_view is larger than the width of image_view
            image_view_height = self.view_size.height
            image_view_width = int(self.view_size.height * image_view_ratio)
        else:
            # The height of background_view is larger than the height of image_view
            image_view_width = self.view_size.width
            image_view_height = int(self.view_size.width / image_view_ratio)
        image_view_size = Resolution(width=image_view_width, height=image_view_height)
        return image_view_size


    def gui_set(self):
        self.timer_label.place(relx=0.3, rely=0.1, relwidth=0.4, relheight=0.1)
        self.good_points_label.place(relx=0.3, rely=0.2, relwidth=0.4, relheight=0.2)
        self.bad_points_label.place(relx=0.3, rely=0.4, relwidth=0.4, relheight=0.2)
        self.score_label.place(relx=0.3, rely=0.6, relwidth=0.4, relheight=0.2)
        self.full_score_label.place(relx=0.3, rely=0.8, relwidth=0.4, relheight=0.1)
