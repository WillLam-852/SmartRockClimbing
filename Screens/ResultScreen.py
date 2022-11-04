import PIL
import cv2
import i18n
import numpy as np
from tkinter import *

from Models.Enums.CameraOrientation import CAMERA_ORIENTATION
from Models.Enums.Screen import SCREEN
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

    def launch(self, result, gamemode):
        self.settings = SaveLoadModule().load_settings()
        i18n.set('locale', SaveLoadModule().load_locale())
        self.change_title(i18n.t('t.result'))
        self.buttons = {
            0: ControlBarButton(i18n.t('t.view_image'), self.view_image_btn_pressed),
            9: ControlBarButton(i18n.t('t.home'), lambda: self.navigate(SCREEN.HOME), THEME_COLOR_PINK)
        }
        self.change_buttons(self.buttons)

        self.result = result
        self.gamemode = gamemode
        self.show(self.result, self.gamemode)


    def show(self, results, gamemode):
        if gamemode == 2:
            self.timer_label.config(text=f"{i18n.t('t.time')}: {results.get_time()}")
            self.good_points_label.config(text=f"The word you have spelt is:")
            self.bad_points_label.config(text=f"{results.get_word()}")
            self.score_label.config(text="")
            self.full_score_label.config(text="")
        else:
            self.timer_label.config(text=f"{i18n.t('t.time')}: {results.get_time()}")
            self.good_points_label.config(
                text=f'''{i18n.t('t.touch_points')}: {results.get_good_points()[0]} / {results.get_good_points()[1]}
            {i18n.t('t.scores_get')}:   {TOUCHED_GOOD_POINT_WEIGHT} x {results.get_good_points()[0]} = {results.get_score()[0]}''')
            self.bad_points_label.config(
                text=f'''{i18n.t('t.avoid_points')}: {results.get_bad_points()[0]} / {results.get_bad_points()[1]}
            {i18n.t('t.scores_deducted')}: {TOUCHED_BAD_POINT_WEIGHT} x {results.get_bad_points()[0]} = {results.get_score()[1]}''')
            self.score_label.config(text=f"{i18n.t('t.total_score')}: {results.get_score()[2]}")
            self.full_score_label.config(
                text=f"{i18n.t('t.full_score')}: {int(TOUCHED_GOOD_POINT_WEIGHT * results.get_good_points()[1])}")
    # Button Actions

    def view_image_btn_pressed(self):
        self.numpy_img, touched_good_points, untouched_good_points, touched_bad_points, untouched_bad_points = self.result.get_image_and_points()

        if self.settings.mirror_camera:
            self.numpy_img = cv2.flip(self.numpy_img, 1)
        if self.settings.camera_orientation_mode == CAMERA_ORIENTATION.LEFT:
            self.numpy_img = cv2.rotate(self.numpy_img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif self.settings.camera_orientation_mode == CAMERA_ORIENTATION.RIGHT:
            self.numpy_img = cv2.rotate(self.numpy_img, cv2.ROTATE_90_CLOCKWISE)
        elif self.settings.camera_orientation_mode == CAMERA_ORIENTATION.INVERTED:
            self.numpy_img = cv2.rotate(self.numpy_img, cv2.ROTATE_180)

        pose_detection_module = PoseDetectionModule()
        pose_detection_module.update_settings(self.settings)
        image_resolution = Resolution(width=self.numpy_img.shape[1], height=self.numpy_img.shape[0])
        image_view_width, image_view_height = self.gui_image_view_calculate(image_resolution=image_resolution)
        pose_detection_module.update_camera_view(self.result_image_view, image_view_width, image_view_height)
        self.numpy_img = cv2.resize(self.numpy_img, (image_view_width, image_view_height))

        for point in touched_good_points:
            camera_point = pose_detection_module.map_to_camera_point(point)
            cv2.circle(self.numpy_img, camera_point, DOT_RADIUS, TOUCHED_GOOD_POINTS_COLOR, -1)
        for point in untouched_good_points:
            camera_point = pose_detection_module.map_to_camera_point(point)
            cv2.circle(self.numpy_img, camera_point, DOT_RADIUS, GOOD_POINTS_COLOR, -1)
        for point in touched_bad_points:
            camera_point = pose_detection_module.map_to_camera_point(point)
            cv2.circle(self.numpy_img, camera_point, DOT_RADIUS, TOUCHED_BAD_POINTS_COLOR, -1)
        for point in untouched_bad_points:
            camera_point = pose_detection_module.map_to_camera_point(point)
            cv2.circle(self.numpy_img, camera_point, DOT_RADIUS, BAD_POINTS_COLOR, -1)
        
        self.img = PIL.ImageTk.PhotoImage(PIL.Image.fromarray(np.uint8(self.numpy_img)))
        self.result_image_view.config(image=self.img)
        self.result_image_view.place(relx=0.5, rely=0.5, width=image_view_width, height=image_view_height, anchor=CENTER)
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
            9: ControlBarButton(i18n.t('t.home'), lambda: self.navigate(VIEW.HOME), THEME_COLOR_PINK)
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
