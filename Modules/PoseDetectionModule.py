import copy
from tkinter import Label
# import time
import cv2
import datetime
import csv
import mediapipe as mp
# from typing import Any
from PIL import Image, ImageTk

from Models.Enums.CameraMode import CAMERA_MODE
from Models.Enums.CameraOrientation import CAMERA_ORIENTATION
from Models.Enums.CameraState import CAMERA_STATE
from Models.Calculation.CalculationResult import CalculationResult
from Models.Enums.GameMode import GAME_MODE
from Models.Path.Path import Path
from Models.Path.PathImage import PathImage
from Models.Path.Point import Point
from Models.Resolution import Resolution
from Models.Settings.Settings import Settings
from Modules.CalculationModule import CalculationModule
from Utilities.Constants import *
from Utilities.OpenFile import open_file

mp_drawing = mp.solutions.drawing_utils
# mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose


class PoseDetectionModule:

    # Methods for Changing Camera State

    def change_camera_state(self, camera_state: CAMERA_STATE):
        if camera_state == CAMERA_STATE.PLAYING:
            self.calculation_module = None
            self.stop_video_recording()
        elif camera_state == CAMERA_STATE.PAUSE:
            self.calculation_module = CalculationModule(self.pause_image)
        elif camera_state == CAMERA_STATE.RECORDING:
            self.start_video_recording()
        self.camera_state = camera_state


    # Methods for CAMERA_STATE.PAUSE

    def tap_on_screen(self, point: Point) -> CalculationResult:
        calculation_result_with_image = self.calculation_module.calculate(point)
        self.shown_image = calculation_result_with_image.image_with_drawing
        return calculation_result_with_image.calculation_result


    def clear_all_dots(self):
        self.shown_image = self.calculation_module.clear_all_dots()


    # Methods for CAMERA_STATE.RECORDING

    def start_video_recording(self):
        self.video_start_time = datetime.datetime.now()
        file_date_time = self.video_start_time.strftime("%Y%m%d-%H%M%S")

        # Video File Configuration
        video_file_name = open_file(f"{VIDEO_FILES_LOCATION}pose_test{file_date_time}.mp4")
        fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
        if self.settings.camera_orientation_mode == CAMERA_ORIENTATION.LEFT or self.settings.camera_orientation_mode == CAMERA_ORIENTATION.RIGHT:
            resolution = (self.camera_resolution.height, self.camera_resolution.width)
        else:
            resolution = (self.camera_resolution.width, self.camera_resolution.height)
        self.out_video = cv2.VideoWriter(video_file_name, fourcc, RECORDING_FPS, resolution)

        # CSV File Configuration
        csv_file_name = open_file(f"{VIDEO_FILES_LOCATION}pose_test{file_date_time}.csv")
        self.csv_file = open(csv_file_name, "w", encoding='UTF8', newline='')
        self.csv_writer = csv.writer(self.csv_file)

        self.saved_frame_data = []
        if DEBUG_MODE:
            print("Start Recording: " + file_date_time)


    def stop_video_recording(self):
        try:
            # Video File Configuration
            self.out_video.release()

            # CSV File Configuration
            for frame_data in self.saved_frame_data:
                if len(frame_data) == 1:
                    # No pose is detected in this frame
                    self.csv_writer.writerow([f"{frame_data[0][0]}"])
                    self.csv_writer.writerow(["None"])
                else:
                    for part in frame_data:
                        self.csv_writer.writerow(part)
                self.csv_writer.writerow("")
            self.csv_file.close()

            if DEBUG_MODE:
                print("Finish Recording")
        except:
            print("csv_file and outVideo are not defined")


    def record_frame_data(self, image, pose_result):
        # Save in Video File
        try:
            record_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            self.out_video.write(record_image)
        except:
            print("outVideo can't write")

        # Save in CSV File
        time = (datetime.datetime.now() - self.video_start_time).total_seconds()
        frame_data = [[str(datetime.timedelta(seconds=time)), "x", "y"]]
        body_data = self.record_pose_information(pose_result.pose_landmarks)
        if body_data:
            frame_data += body_data
        self.saved_frame_data.append(frame_data)


    def record_pose_information(self, pose_landmarks) -> list[list[str]]:
        if pose_landmarks:
            nose = self.get_body_point(pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE])
            left_index = self.get_body_point(pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_INDEX])
            right_index = self.get_body_point(pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_INDEX])
            left_elbow = self.get_body_point(pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW])
            right_elbow = self.get_body_point(pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW])
            left_shoulder = self.get_body_point(pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER])
            right_shoulder = self.get_body_point(pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER])
            left_hip = self.get_body_point(pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP])
            right_hip = self.get_body_point(pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP])
            left_knee = self.get_body_point(pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE])
            right_knee = self.get_body_point(pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE])
            left_ankle = self.get_body_point(pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE])
            right_ankle = self.get_body_point(pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE])
            frame_data = []
            frame_data.append(self.create_frame_data("Head", nose))
            frame_data.append(self.create_frame_data("Left Hand", left_index))
            frame_data.append(self.create_frame_data("Right Hand", right_index))
            frame_data.append(self.create_frame_data("Left Elbow", left_elbow))
            frame_data.append(self.create_frame_data("Right Elbow", right_elbow))
            frame_data.append(self.create_frame_data("Left Shoulder", left_shoulder))
            frame_data.append(self.create_frame_data("Right Shoulder", right_shoulder))
            frame_data.append(self.create_frame_data("Left Hip", left_hip))
            frame_data.append(self.create_frame_data("Right Hip", right_hip))
            frame_data.append(self.create_frame_data("Left Knee", left_knee))
            frame_data.append(self.create_frame_data("Right Knee", right_knee))
            frame_data.append(self.create_frame_data("Left Ankle", left_ankle))
            frame_data.append(self.create_frame_data("Right Ankle", right_ankle))
            frame_data.append(["Angles"])
            frame_data.append(["Left Hand - Left Elbow - Left Shoulder", self.calculate_angle(left_index, left_elbow, left_shoulder)])
            frame_data.append(["Right Hand - Right Elbow - Right Shoulder", self.calculate_angle(right_index, right_elbow, right_shoulder)])
            frame_data.append(["Left Elbow - Left Shoulder - Left Hip", self.calculate_angle(left_elbow, left_shoulder, left_hip)])
            frame_data.append(["Right Elbow - Right Shoulder - Right Hip", self.calculate_angle(right_elbow, right_shoulder, right_hip)])
            frame_data.append(["Left Hip - Left Knee - Left Ankle", self.calculate_angle(left_hip, left_knee, left_ankle)])
            frame_data.append(["Right Hip - Right Knee - Right Ankle", self.calculate_angle(right_hip, right_knee, right_ankle)])
            return frame_data
        else:
            return None


    def get_body_point(self, result) -> Point:
        x = int(result.x * self.camera_view_size.width)
        y = int(result.y * self.camera_view_size.height)
        return Point(x=x, y=y)


    def create_frame_data(self, name: str, point: Point):
        frame_data = [name, point.x, point.y]
        return frame_data
    

    def calculate_angle(self, pt1: Point, pt2: Point, pt3: Point) -> str:
        calculation_module = CalculationModule()
        angle = calculation_module.find_angle_between_three_points(pt1, pt2, pt3)
        return "{:.2f}".format(angle)




    # Methods for Setting up and Stopping Camera

    def get_camera_resolution(self, camera_number: int) -> Resolution:
        try:
            cap = cv2.VideoCapture(camera_number, cv2.CAP_DSHOW)
            cap.read()

            if DEBUG_MODE:
                if CAMERA_RESOLUTION_WIDTH:
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_RESOLUTION_WIDTH)
                if CAMERA_RESOLUTION_HEIGHT:
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_RESOLUTION_HEIGHT)


            if int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) == 0 or int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) == 0:
                cap.release()
                return None

            camera_resolution = Resolution(width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            if DEBUG_MODE:
                print(f"Camera Resolution: {camera_resolution.width}x{camera_resolution.height}")

            cap.release()
            return camera_resolution

        except:
            # No camera is detected
            print("ERROR: No camera is detected")
            cap.release()
            return None


    def set_camera_input(self, camera_view: Label, camera_view_size: Resolution, camera_number: int, camera_resolution: Resolution, settings: Settings):
        self.cap = cv2.VideoCapture(camera_number, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, camera_resolution.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_resolution.height)
        self.camera_resolution = camera_resolution
        self.update_camera_view(camera_view=camera_view, size=camera_view_size)
        # self.sound_module = SoundModule()
        self.pose = mp_pose.Pose(
            min_detection_confidence=0.5,   
            min_tracking_confidence=0.5
        )
        self.camera_state = CAMERA_STATE.PLAYING
        self.camera_mode = CAMERA_MODE.NORMAL
        self.settings = settings
        self.is_distance_calibration_shown = False


    def update_settings(self, settings: Settings, is_distance_calibration_shown=False):
        self.settings = settings
        self.is_distance_calibration_shown = is_distance_calibration_shown


    def update_camera_view(self, camera_view: Label, size: Resolution):
        self.camera_view = camera_view
        self.camera_view_size = size


    # Methods of Mapping Points
    
    def map_to_camera_point(self, universal_point: Point) -> Point:
        """
        Translate a universal point (saved in .csv file) to a camera point (touch on screen)
        
        Parameters
        ----------
        universal_point: Point
            universal point (saved in .csv file)
        """
        x, y = float(universal_point.x), float(universal_point.y)
        width, height = float(self.camera_view_size.width), float(self.camera_view_size.height)
        if self.settings.camera_orientation_mode == CAMERA_ORIENTATION.LEFT or self.settings.camera_orientation_mode == CAMERA_ORIENTATION.RIGHT:
            width, height = height, width
        x, y = x * width, y * height
        if self.settings.camera_orientation_mode == CAMERA_ORIENTATION.LEFT:
            x, y = y, width - x
        elif self.settings.camera_orientation_mode == CAMERA_ORIENTATION.RIGHT:
            x, y = height - y, x
        elif self.settings.camera_orientation_mode == CAMERA_ORIENTATION.INVERTED:
            x, y = width - x, height - y
        if self.settings.is_mirror_camera:
            x = float(self.camera_view_size.width) - x
        return Point(x=int(x), y=int(y), is_good=universal_point.is_good, order=universal_point.order, alphabet=universal_point.alphabet)


#     def map_to_spelling_point(self, point_sequence):
#         width, height = self.camera_view_width / 10, self.camera_view_height * 9 / 10
#         if self.settings.camera_orientation_mode == CAMERA_ORIENTATION.LEFT or self.settings.camera_orientation_mode == CAMERA_ORIENTATION.RIGHT:
#             width, height = height, width
#         width, height = int(width + 50*point_sequence), int(height)
#         return (width, height)


    def map_to_universal_point(self, camera_point: Point) -> Point:
        """
        Translate a camera point (touch on screen) to a universal point (saved in .csv file)
        
        Parameters
        ----------
        camera_point: Point
            Point that user touches on screen
        """
        x, y = float(camera_point.x), float(camera_point.y)
        print("x, y", x, y)
        width, height = float(self.camera_view_size.width), float(self.camera_view_size.height)
        print("width, height", width, height)
        if self.settings.is_mirror_camera:
            x = width - x
        if self.settings.camera_orientation_mode == CAMERA_ORIENTATION.LEFT:
            x, y = height - y, x
            width, height = height, width
        elif self.settings.camera_orientation_mode == CAMERA_ORIENTATION.RIGHT:
            x, y = y, width - x
            width, height = height, width
        elif self.settings.camera_orientation_mode == CAMERA_ORIENTATION.INVERTED:
            x, y = width - x, height - y
        print("before division x, y", x, y)
        x, y = x / width, y / height
        print("after division x, y", x, y)
        return Point(x=int(x), y=int(y), is_good=camera_point.is_good, order=camera_point.order, alphabet=camera_point.alphabet)


    # Game Mode Methods

    # def game_start(self, path_id, points: list[Point], gamemode, progress_callback):
    #     self.camera_mode = CAMERA_MODE.GAME
    #     self.path_id = path_id
    #     self.universal_points = points
    #     self.universal_points_history = [self.universal_points.copy()]
    #     self.redo_history = []
    #     self.gamemode = gamemode
    #     self.is_good_points_shown = False
    #     self.is_bad_points_shown = False
    #     self.update_progress_label = progress_callback
    #     self.spelling_point_list = []
    #     self.point_index = 0
    #     self.foot_touch_ground_time = 0
    #     self.time_threshold = 100
    #     self.then = time.time_ns() // 1_000_000
    #     self.test_frames = []
    #     self.game_test_frame_rate()


#     def game_toggle_show_good_points(self, is_shown):
#         self.is_good_points_shown = is_shown


#     def game_toggle_show_bad_points(self, is_shown):
#         self.is_bad_points_shown = is_shown


#     def game_calculate_pose(self, path, pose_landmarks):
#         if path and pose_landmarks:
#             left_index = self.get_body_point(pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_INDEX])
#             right_index = self.get_body_point(pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_INDEX])
#             left_ankle = self.get_body_point(pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE])
#             right_ankle = self.get_body_point(pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE])
#             for body_point in [left_index, right_index, left_ankle, right_ankle]:
#                 universal_point = self.map_to_universal_point(body_point)
#                 self.path.evaluate_body_point(universal_point)


#     def game_update_progress_label(self, path):
#         if path:
#             if self.gamemode == GAME_MODE.OBSTACLE or self.gamemode == GAME_MODE.SEQUENCE:
#                 self.update_progress_label(len(path.touched_good_points), len(path.good_points))
#             elif self.gamemode == GAME_MODE.ALPHABET:
#                 self.update_progress_label(len(path.player_input_alphabets), 0)
            

#     def game_show_game_points(self, path, gamemode):
#         if path:
#             if self.is_good_points_shown:
#                 for point in self.path.good_points:
#                     camera_point = self.map_to_camera_point(point)
#                     cv2.circle(self.resized_image, camera_point, DOT_RADIUS, GOOD_POINTS_COLOR, -1)
#                 for point in self.path.touching_good_points:
#                     camera_point = self.map_to_camera_point(point)
#                     cv2.circle(self.resized_image, camera_point, DOT_RADIUS, TOUCHING_GOOD_POINTS_COLOR, -1)
#                 for point in self.path.touched_good_points:
#                     camera_point = self.map_to_camera_point(point)
#                     cv2.circle(self.resized_image, camera_point, DOT_RADIUS, TOUCHED_GOOD_POINTS_COLOR, -1)
#                 for point in self.path.good_points:
#                     if gamemode == GAME_MODE.SEQUENCE:
#                         cv2.putText(self.resized_image, str(point[3]+1), camera_point, POINT_FONTFACE, POINT_FONTSCALE, POINT_TEXT_COLOR, POINT_TEXT_THICKNESS)
#                     elif gamemode == GAME_MODE.ALPHABET:
#                         cv2.putText(self.resized_image, str(point[4]), camera_point, POINT_FONTFACE, POINT_FONTSCALE, POINT_TEXT_COLOR, POINT_TEXT_THICKNESS)
#             if gamemode == GAME_MODE.OBSTACLE and self.is_bad_points_shown:
#                 for point in self.path.bad_points:
#                     camera_point = self.map_to_camera_point(point)
#                     cv2.circle(self.resized_image, camera_point, DOT_RADIUS, BAD_POINTS_COLOR, -1)
#                 for point in self.path.touching_bad_points:
#                     camera_point = self.map_to_camera_point(point)
#                     cv2.circle(self.resized_image, camera_point, DOT_RADIUS, TOUCHING_BAD_POINTS_COLOR, -1)
#                 for point in self.path.touched_bad_points:
#                     camera_point = self.map_to_camera_point(point)
#                     cv2.circle(self.resized_image, camera_point, DOT_RADIUS, TOUCHED_BAD_POINTS_COLOR, -1)


#     def game_show_alphabets(self, path, point_index):
#         if path:
#             if len(self.universal_points) > 0 and len(path.player_input_alphabets) > 0:
#                 for point in path.player_input_alphabets:
#                     if point_index < len(path.player_input_alphabets):
#                         spelling_point = self.map_to_spelling_point(point_index)
#                         self.point_index = point_index + 1
#                     else:
#                         spelling_point = self.map_to_spelling_point(0)
#                         self.point_index = 1
#                     if spelling_point not in self.spelling_point_list:
#                         self.spelling_point_list.append(spelling_point)
#                         cv2.putText(self.resized_image, str(point[1][4]),
#                                     org=self.spelling_point_list[point[0]],
#                                     fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=3, color=(0, 255, 255),
#                                     thickness=3)

#     def game_finish(self):
#         result = self.path.evaluate_result()
#         self.toggle_record_video(False)
#         return result


#     def game_test_frame_rate(self):
#         if self.cap.isOpened():                
#             # Read the webcam input from openCV
#             success, image = self.cap.read()
#             if not success:
#                 print("Ignoring empty camera frame.")
#                 return

#             # To improve performance, optionally mark the image as not writeable to
#             # pass by reference.
#             image.flags.writeable = False

#             # Setting the image
#             image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#             if self.settings.camera_orientation_mode == CAMERA_ORIENTATION.LEFT:
#                 image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
#             elif self.settings.camera_orientation_mode == CAMERA_ORIENTATION.RIGHT:
#                 image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
#             elif self.settings.camera_orientation_mode == CAMERA_ORIENTATION.INVERTED:
#                 image = cv2.rotate(image, cv2.ROTATE_180)
#             if self.settings.mirror_camera:
#                 image = cv2.flip(image, 1)

#             # Process the image with Mediapipe AI Model
#             results = self.pose.process(image)

#             # Mark the pose with landmarks
#             image.flags.writeable = True

#             mp_drawing.draw_landmarks(
#                 image=image,
#                 landmark_list=results.pose_landmarks,
#                 connections=[
#                     (11,12),                                # Head
#                     (11,23), (12,24), (23,24),              # Core Body
#                     (11,13), (13,15), (15,19),              # Left Arm
#                     (12,14), (14,16), (16,20),              # Right Arm
#                     (23,25), (25,27), (27,29), (29,31),     # Left Leg
#                     (24,26), (26,28), (28,30), (30,32)      # Right Leg
#                 ],
#                 landmark_drawing_spec=mp_drawing.DrawingSpec(
#                     color=LANDMARK_COLOR,
#                     thickness=LANDMARK_THICKNESS,
#                     circle_radius=LANDMAKR_CIRCLE_RADIUS
#                 ),
#                 connection_drawing_spec=mp_drawing.DrawingSpec(
#                     color=CONNECTION_COLOR,
#                     thickness=CONNECTION_THICKNESS,
#                     circle_radius=CONNECTION_CIRCLE_RADIUS
#                 )
#             )

#             # Resize image to fit camera view size
#             self.resized_image = cv2.resize(image.copy(), (self.camera_view_width, self.camera_view_height))
#             self.image = self.resized_image.copy()

#             # Send the image back to tkinter class (MetaHub)
#             pilImg = Image.fromarray(self.image)
#             imgtk = ImageTk.PhotoImage(image=pilImg)
#             self.camera_view.imgtk = imgtk
#             self.camera_view.configure(image=imgtk)

#             # Calculate time between frames
#             self.now = time.time_ns() // 1_000_000 # time in milliseconds
#             delta = self.now - self.then # time difference between current frame and previous frame
#             self.then = self.now
#             self.test_frames.append(delta/1000)

#             if len(self.test_frames) < 10:
#                 self.camera_view.after(int(1000 / SET_CAMERA_FPS), self.game_test_frame_rate)
#             else:
#                 self.test_frames.pop(0)
#                 average_time_between_frames = sum(self.test_frames) / len(self.test_frames)
#                 if DEBUG_MODE:
#                     print("average_time_between_frames:", average_time_between_frames)
#                 self.path = Path(self.path_id, self.universal_points, self.gamemode, average_time_between_frames)
#                 self.sound_module.countdown()


    # Setting Game Path Methods

    def settings_start(self, path: Path):
        self.camera_mode = CAMERA_MODE.SETTINGS
        self.path: Path = path
        self.universal_points_history: list[list[Point]] = [self.path.points.copy()]
        self.redo_history: list[list[Point]] = []


    def settings_screen_pressed(self, point: Point):
        print("point:", point.x, point.y)
        new_universal_point = self.map_to_universal_point(camera_point=point)
        print("new_universal_point:", new_universal_point.x, new_universal_point.y)
        new_universal_points = self.universal_points_history[-1] + [new_universal_point]
        self.universal_points_history.append(new_universal_points)
        self.redo_history.clear()
        self.path.update_points(points=new_universal_points)
        

    def settings_undo(self):
        if len(self.universal_points_history) > 1:
            old_universal_points = self.universal_points_history.pop().copy()
            new_universal_points = self.universal_points_history[-1].copy()
            self.redo_history.append(old_universal_points)
            self.path.update_points(points=new_universal_points)


    def settings_redo(self):
        if len(self.redo_history) > 0:
            new_universal_points = self.redo_history.pop().copy()
            self.universal_points_history.append(new_universal_points)
            self.path.update_points(points=new_universal_points)


    def settings_clear_all_points(self):
        universal_points = self.universal_points_history[-1].copy()
        if len(universal_points) > 0:
            new_universal_points: list[Point] = []
            self.universal_points_history.append(new_universal_points)
            self.redo_history.clear()
            self.path.update_points(points=new_universal_points)


    def settings_show_game_points(self):
        if self.path.game_mode == GAME_MODE.OBSTACLE:
            for good_point in self.path.good_points:
                print("good_point:", good_point.x, good_point.y)
                good_camera_point = self.map_to_camera_point(universal_point=good_point)
                print("good_camera_point:", good_camera_point.x, good_camera_point.y)
                cv2.circle(self.resized_image, (good_camera_point.x, good_camera_point.y), DOT_RADIUS, GOOD_POINTS_COLOR, -1)
            for bad_point in self.path.bad_points:
                bad_camera_point = self.map_to_camera_point(bad_point)
                cv2.circle(self.resized_image, (bad_camera_point.x, bad_camera_point.y), DOT_RADIUS, BAD_POINTS_COLOR, -1)

        elif self.gamemode == GAME_MODE.SEQUENCE:
            for point in self.path.points:
                camera_point = self.map_to_camera_point(universal_point=point)
                cv2.circle(self.resized_image, (camera_point.x, camera_point.y), DOT_RADIUS, GOOD_POINTS_COLOR, -1)
                cv2.putText(self.resized_image, str(point.order+1), (camera_point.x, camera_point.y), POINT_FONTFACE, POINT_FONTSCALE, POINT_TEXT_COLOR, POINT_TEXT_THICKNESS)
        
        elif self.gamemode == GAME_MODE.ALPHABET:
            for point in self.path.points:
                camera_point = self.map_to_camera_point(universal_point=point)
                cv2.circle(self.resized_image, (camera_point.x, camera_point.y), DOT_RADIUS, GOOD_POINTS_COLOR, -1)
                cv2.putText(self.resized_image, point.alphabet, (camera_point.x, camera_point.y), POINT_FONTFACE, POINT_FONTSCALE, POINT_TEXT_COLOR, POINT_TEXT_THICKNESS)


    def settings_done(self) -> tuple[Path, PathImage]:
        saved_image = cv2.cvtColor(self.saved_image, cv2.COLOR_RGB2BGR)
        if self.settings.is_mirror_camera:
            saved_image = cv2.flip(saved_image, 1)

        if self.settings.camera_orientation_mode == CAMERA_ORIENTATION.LEFT:
            saved_image = cv2.rotate(saved_image, cv2.ROTATE_90_CLOCKWISE)
        elif self.settings.camera_orientation_mode == CAMERA_ORIENTATION.RIGHT:
            saved_image = cv2.rotate(saved_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif self.settings.camera_orientation_mode == CAMERA_ORIENTATION.INVERTED:
            saved_image = cv2.rotate(saved_image, cv2.ROTATE_180)

        path_image = PathImage(path_id=self.path.id, image=saved_image)
        return tuple[self.path, path_image]


    def camera_input(self):
        """
        Start webcam input & pose detection (Call Repeatedly)
        """
        if self.cap.isOpened():
            # Read the webcam input from openCV
            success, image = self.cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                return

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False

            # Setting the image
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            if self.settings.camera_orientation_mode == CAMERA_ORIENTATION.LEFT:
                image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
            elif self.settings.camera_orientation_mode == CAMERA_ORIENTATION.RIGHT:
                image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
            elif self.settings.camera_orientation_mode == CAMERA_ORIENTATION.INVERTED:
                image = cv2.rotate(image, cv2.ROTATE_180)
            if self.settings.is_mirror_camera:
                image = cv2.flip(image, 1)

            # Process the image with Mediapipe AI Model
            results = self.pose.process(image)

            # Mark the pose with landmarks
            image.flags.writeable = True

            shown_landmarks = copy.copy(results.pose_landmarks)
            if shown_landmarks:
                del shown_landmarks.landmark[29:33]
                del shown_landmarks.landmark[21:23]
                del shown_landmarks.landmark[15:19]
                del shown_landmarks.landmark[1:11]

            mp_drawing.draw_landmarks(
                image=image,
                landmark_list=shown_landmarks,
                connections=[
                    (1, 2), (1, 7), (2, 8), (7, 8),       # Core Body
                    (1, 3), (3, 5),                       # Left Arm
                    (2, 4), (4, 6),                       # Right Arm
                    (7, 9), (9, 11),                      # Left Leg
                    (8, 10), (10, 12)                     # Right Leg
                ],
                landmark_drawing_spec=mp_drawing.DrawingSpec(
                    color=LANDMARK_COLOR,
                    thickness=LANDMARK_THICKNESS,
                    circle_radius=LANDMAKR_CIRCLE_RADIUS
                ),
                connection_drawing_spec=mp_drawing.DrawingSpec(
                    color=CONNECTION_COLOR,
                    thickness=CONNECTION_THICKNESS,
                    circle_radius=CONNECTION_CIRCLE_RADIUS
                )
            )

            if self.camera_state == CAMERA_STATE.RECORDING:
                self.record_frame_data(image=image, pose_result=results)
                

#             # For danger alert
#             if self.camera_mode != CAMERA_MODE.SETTINGS and self.show_danger_alert:
#                 if self.settings.danger_alert and results.pose_landmarks:
#                     left_index = self.get_body_point(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_INDEX])
#                     right_index = self.get_body_point(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_INDEX])
#                     left_ankle = self.get_body_point(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE])
#                     right_ankle = self.get_body_point(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE])
#                     if left_index < left_ankle and right_index > right_ankle:
#                         self.sound_module.danger_alert()
#                         self.show_danger_alert(True)
#                     else:
#                         self.show_danger_alert(False)
#                 else:
#                     self.show_danger_alert(False)

#             if self.camera_mode == CAMERA_MODE.GAME:
#                 if len(self.universal_points) > 0:
#                     if self.gamemode == GAME_MODE.ALPHABET:
#                         if results.pose_landmarks:
#                             left_foot = self.get_body_point(
#                                 results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_FOOT_INDEX])
#                             right_foot = self.get_body_point(
#                                 results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX])
#                             if self.camera_view_height * self.ground_screen_ratio <= left_foot[
#                                 1] <= self.camera_view_height and self.camera_view_height * self.ground_screen_ratio <= \
#                                     right_foot[1] <= self.camera_view_height:
#                                 self.foot_touch_ground_time += 1
#                                 if self.foot_touch_ground_time > self.time_threshold:
#                                     self.update_progress_label(len(self.path.player_input_alphabets),
#                                                            -1,
#                                                            self.universal_points[0][5])
#                                     self.foot_touch_ground_time = 0

            # Resize image to fit camera view size
            self.resized_image = cv2.resize(image.copy(), (self.camera_view_size.width, self.camera_view_size.height))

#             # For Debugging, use mouse to simulate body point
#             if DEBUG_MODE:
#                 if self.debug_body_point:
#                     cv2.circle(self.resized_image, self.debug_body_point, DOT_RADIUS, (0, 0, 255), -1)
#                     if self.camera_mode == CAMERA_MODE.GAME:
#                         debug_body_universal_point = self.map_to_universal_point(self.debug_body_point)
#                         self.path.evaluate_body_point(debug_body_universal_point)

#             if self.camera_mode == CAMERA_MODE.GAME:
#                 # Calculate Pose (Game)
#                 self.game_calculate_pose(self.path, results.pose_landmarks)
#                 self.game_update_progress_label(self.path)
#                 # Show Game Points (Game)
#                 self.game_show_game_points(self.path, self.gamemode)
#                 if self.gamemode == GAME_MODE.ALPHABET:
#                     self.game_show_alphabets(self.path)

            # Show Game Points (Settings)
            if self.camera_mode == CAMERA_MODE.SETTINGS:
                self.settings_show_game_points()

#             # If Calibration is on,
#             #   show a yellow horizontal line with CALIBRATION_PIXELS (default: 100)
#             #   and a white horizontal line for ground level
            if self.is_distance_calibration_shown:
                # Draw middle distance calibration line
                cv2.line(self.resized_image, (int(self.camera_view_size.width/2-CALIBRATION_PIXELS/2), int(self.camera_view_size.height/2)), (int(self.camera_view_size.width/2+CALIBRATION_PIXELS/2), int(self.camera_view_size.height/2)), RGB_COLOR_YELLOW, 5)
                # Draw ground level line
                ground_level = self.camera_view_size.height * self.settings.ground_ratio_calibration_actual_value
                cv2.line(self.resized_image, (int(0), int(ground_level)), (int(self.camera_view_size.width), int(ground_level)), RGB_COLOR_WHITE, 5)

            # If camera_state is not pause, copy the image to be used later
            if self.camera_state != CAMERA_STATE.PAUSE:
                self.pause_image = self.resized_image.copy()
                self.shown_image = self.resized_image.copy()

            # Send the image back to tkinter class (CameraView or SettingsView)
            pilImg = Image.fromarray(self.shown_image)
            imgtk = ImageTk.PhotoImage(image=pilImg)
            self.camera_view.imgtk = imgtk
            self.camera_view.configure(image=imgtk)
            self.camera_view.after(int(1000 / SET_CAMERA_FPS), self.camera_input)


    def stop_camera_input(self):
        try:
            self.cap.release()
            if DEBUG_MODE:
                print("Stop Camera")
        except:
            print("ERROR: Cannot Stop Camera")



    # Debug Methods

    def simulate_body_point(self, point=None):
        if point:
            self.debug_body_point = point
        else:
            self.debug_body_point = None
