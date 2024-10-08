from __future__ import annotations
import copy
import csv
import cv2
import datetime
import mediapipe as mp
import time
from PIL import Image, ImageTk
from tkinter import Label

from Models.Calculation.CalculationResult import CalculationResult
from Models.Enums.CameraMode import CAMERA_MODE
from Models.Enums.CameraOrientation import CAMERA_ORIENTATION
from Models.Enums.CameraState import CAMERA_STATE
from Models.Enums.GameMode import GAME_MODE
from Models.Path.GamePath import GamePath
from Models.Path.Path import Path
from Models.Path.PathImage import PathImage
from Models.Path.Point import Point
from Models.Resolution import Resolution
from Models.Settings.Settings import Settings
from Modules.CalculationModule import CalculationModule
from Modules.SaveLoadModule import SaveLoadModule
from Modules.SoundModule import SoundModule
from Utilities.Constants import *
from Utilities.OpenFile import open_file

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


class PoseDetectionModule:

    # Methods (for ALL Camera Mode)

    # Methods for Starting Camera

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
                self.debug_game_camera_point = None

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
        self.sound_module = SoundModule()
        self.pose = mp_pose.Pose(
            min_detection_confidence=0.5,   
            min_tracking_confidence=0.5
        )
        self.camera_state = CAMERA_STATE.PLAYING
        self.camera_mode = CAMERA_MODE.NORMAL
        self.settings = settings


    def update_camera_view(self, camera_view: Label, size: Resolution):
        self.camera_view = camera_view
        self.camera_view_size = size


    # Methods for Camera Input

    def camera_input(self):
        """
        Start webcam input & pose detection (Call Repeatedly)
        """
        if self.cap.isOpened():
            self.camera_input_image_processing(is_test=False)
            # Send the image back to tkinter class (CameraView or SettingsView)
            pilImg = Image.fromarray(self.shown_image)
            imgtk = ImageTk.PhotoImage(image=pilImg)
            self.camera_view.imgtk = imgtk
            self.camera_view.configure(image=imgtk)
            self.camera_view.after(int(1000 / SET_CAMERA_FPS), self.camera_input)


    def camera_input_image_processing(self, is_test: bool=False):
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

        if not is_test:
            if self.camera_state == CAMERA_STATE.RECORDING:
                self.recording_proceed_frame(image=image, pose_result=results)
                

                # # For danger alert
                # if self.camera_mode != CAMERA_MODE.SETTINGS and self.show_danger_alert:
                #     if self.settings.danger_alert and results.pose_landmarks:
                #         left_index = self.get_body_point(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_INDEX])
                #         right_index = self.get_body_point(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_INDEX])
                #         left_ankle = self.get_body_point(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE])
                #         right_ankle = self.get_body_point(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE])
                #         if left_index < left_ankle and right_index > right_ankle:
                #             self.sound_module.danger_alert()
                #             self.show_danger_alert(True)
                #         else:
                #             self.show_danger_alert(False)
                #     else:
                #         self.show_danger_alert(False)

                # if self.camera_mode == CAMERA_MODE.GAME:
                #     if len(self.universal_points) > 0:
                #         if self.gamemode == GAME_MODE.ALPHABET:
                #             if results.pose_landmarks:
                #                 left_foot = self.get_body_point(
                #                     results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_FOOT_INDEX])
                #                 right_foot = self.get_body_point(
                #                     results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX])
                #                 if self.camera_view_height * self.ground_screen_ratio <= left_foot[
                #                     1] <= self.camera_view_height and self.camera_view_height * self.ground_screen_ratio <= \
                #                         right_foot[1] <= self.camera_view_height:
                #                     self.foot_touch_ground_time += 1
                #                     if self.foot_touch_ground_time > self.time_threshold:
                #                         self.update_progress_label(len(self.path.player_input_alphabets),
                #                                                -1,
                #                                                self.universal_points[0][5])
                #                         self.foot_touch_ground_time = 0

        # Resize image to fit camera view size
        self.resized_image = cv2.resize(image.copy(), (self.camera_view_size.width, self.camera_view_size.height))

        if not is_test:
            if self.camera_mode == CAMERA_MODE.GAME:
                self.game_show_game_points()
                if self.game_path.path.game_mode == GAME_MODE.ALPHABET:
                    self.game_show_alphabets()

                self.game_calculate_pose(results.pose_landmarks)
                self.game_update_progress_label(game_path=self.game_path)

                # For Debugging, use mouse to simulate body point
                if DEBUG_MODE and self.debug_game_camera_point:
                    cv2.circle(self.resized_image, (int(self.debug_game_camera_point.x), int(self.debug_game_camera_point.y)), DOT_RADIUS, (0, 0, 255), -1)
                    debug_game_universal_body_point = self.map_to_universal_point(self.debug_game_camera_point)
                    self.game_path.game_evaluate_body_point(universal_body_point=debug_game_universal_body_point)

            # Show Game Points (Settings)
            elif self.camera_mode == CAMERA_MODE.SETTINGS:
                self.settings_show_game_points()

                # If Calibration is on,
                #   show a yellow horizontal line with CALIBRATION_PIXELS (default: 100)
                #   and a white horizontal line for ground level
                if self.settings_is_distance_calibration_shown:
                    # Draw middle distance calibration line
                    cv2.line(self.resized_image, (int(self.camera_view_size.width/2-CALIBRATION_PIXELS/2), int(self.camera_view_size.height/2)), (int(self.camera_view_size.width/2+CALIBRATION_PIXELS/2), int(self.camera_view_size.height/2)), RGB_COLOR_YELLOW, 5)
                    # Draw ground level line
                    ground_level = self.camera_view_size.height * self.settings.ground_ratio_calibration_actual_value
                    cv2.line(self.resized_image, (int(0), int(ground_level)), (int(self.camera_view_size.width), int(ground_level)), RGB_COLOR_WHITE, 5)

        # If camera_state is not pause, copy the image to be used later
        if self.camera_state != CAMERA_STATE.PAUSE:
            self.pause_image = self.resized_image.copy()
            self.shown_image = self.resized_image.copy()


    # Methods for Stopping Camera

    def stop_camera_input(self):
        self.change_camera_state(CAMERA_STATE.PLAYING)
        try:
            self.cap.release()
            if DEBUG_MODE:
                print("Stop Camera")
        except:
            print("ERROR: Cannot Stop Camera")


    # Methods for Point Processing

    def get_body_point(self, result) -> Point:
        x = float(result.x) * self.camera_view_size.width
        y = float(result.y) * self.camera_view_size.height
        return Point(x=x, y=y)


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
        return Point(x=x, y=y, is_good=universal_point.is_good, order=universal_point.order, alphabet=universal_point.alphabet)


    def map_to_universal_point(self, camera_point: Point) -> Point:
        """
        Translate a camera point (touch on screen) to a universal point (saved in .csv file)
        
        Parameters
        ----------
        camera_point: Point
            Point that user touches on screen
        """
        x, y = float(camera_point.x), float(camera_point.y)
        width, height = float(self.camera_view_size.width), float(self.camera_view_size.height)
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
        x, y = x / width, y / height
        return Point(x=x, y=y, is_good=camera_point.is_good, order=camera_point.order, alphabet=camera_point.alphabet)


    # Methods for Changing Camera State

    def change_camera_state(self, camera_state: CAMERA_STATE):
        if camera_state == CAMERA_STATE.PLAYING:
            self.calculation_module = None
            self.recording_stop()
        elif camera_state == CAMERA_STATE.PAUSE:
            self.calculation_module = CalculationModule(self.pause_image)
        elif camera_state == CAMERA_STATE.RECORDING:
            self.recording_start()
        self.camera_state = camera_state


    # Methods (for RECORDING Camera State)

    def recording_start(self):
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


    def recording_stop(self):
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


    def recording_proceed_frame(self, image, pose_result):
        # Save in Video File
        try:
            record_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            self.out_video.write(record_image)
        except:
            print("outVideo can't write")

        # Save in CSV File
        time = (datetime.datetime.now() - self.video_start_time).total_seconds()
        frame_data = [[str(datetime.timedelta(seconds=time)), "x", "y"]]
        body_data = self.recording_pose_information(pose_result.pose_landmarks)
        if body_data:
            frame_data += body_data
        self.saved_frame_data.append(frame_data)


    def recording_pose_information(self, pose_landmarks) -> list[list[str]]:
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
            frame_data.append(self.recording_create_frame_data("Head", nose))
            frame_data.append(self.recording_create_frame_data("Left Hand", left_index))
            frame_data.append(self.recording_create_frame_data("Right Hand", right_index))
            frame_data.append(self.recording_create_frame_data("Left Elbow", left_elbow))
            frame_data.append(self.recording_create_frame_data("Right Elbow", right_elbow))
            frame_data.append(self.recording_create_frame_data("Left Shoulder", left_shoulder))
            frame_data.append(self.recording_create_frame_data("Right Shoulder", right_shoulder))
            frame_data.append(self.recording_create_frame_data("Left Hip", left_hip))
            frame_data.append(self.recording_create_frame_data("Right Hip", right_hip))
            frame_data.append(self.recording_create_frame_data("Left Knee", left_knee))
            frame_data.append(self.recording_create_frame_data("Right Knee", right_knee))
            frame_data.append(self.recording_create_frame_data("Left Ankle", left_ankle))
            frame_data.append(self.recording_create_frame_data("Right Ankle", right_ankle))
            frame_data.append(["Angles"])
            frame_data.append(["Left Hand - Left Elbow - Left Shoulder", self.recording_calculate_angle(left_index, left_elbow, left_shoulder)])
            frame_data.append(["Right Hand - Right Elbow - Right Shoulder", self.recording_calculate_angle(right_index, right_elbow, right_shoulder)])
            frame_data.append(["Left Elbow - Left Shoulder - Left Hip", self.recording_calculate_angle(left_elbow, left_shoulder, left_hip)])
            frame_data.append(["Right Elbow - Right Shoulder - Right Hip", self.recording_calculate_angle(right_elbow, right_shoulder, right_hip)])
            frame_data.append(["Left Hip - Left Knee - Left Ankle", self.recording_calculate_angle(left_hip, left_knee, left_ankle)])
            frame_data.append(["Right Hip - Right Knee - Right Ankle", self.recording_calculate_angle(right_hip, right_knee, right_ankle)])
            return frame_data
        else:
            return None


    def recording_create_frame_data(self, name: str, point: Point):
        frame_data = [name, point.x, point.y]
        return frame_data


    def recording_calculate_angle(self, pt1: Point, pt2: Point, pt3: Point) -> str:
        calculation_module = CalculationModule()
        angle = calculation_module.find_angle_between_three_points(pt1, pt2, pt3)
        return "{:.2f}".format(angle)


    # Methods (for PAUSE Camera State)

    def normal_pause_tap_on_screen(self, point: Point) -> CalculationResult:
        calculation_result_with_image = self.calculation_module.calculate(point)
        self.shown_image = calculation_result_with_image.image_with_drawing
        return calculation_result_with_image.calculation_result


    def normal_pause_clear_all_dots(self):
        self.shown_image = self.calculation_module.clear_all_dots()


    # Methods (for GAME Camera Mode)

    def game_start(self, path: Path, progress_callback):
        self.camera_mode = CAMERA_MODE.GAME
        self.game_path = GamePath(path=path)
        self.game_progress_callback = progress_callback
        # self.spelling_point_list = []
        # self.point_index = 0
        # self.foot_touch_ground_time = 0
        # self.time_threshold = 100
        self.game_test_time_then = time.time_ns() // 1_000_000
        self.game_test_frames = []
        self.game_test_frame_rate()


    def game_calculate_pose(self, pose_landmarks):
        if pose_landmarks:
            left_index = self.get_body_point(pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_INDEX])
            right_index = self.get_body_point(pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_INDEX])
            left_ankle = self.get_body_point(pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE])
            right_ankle = self.get_body_point(pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE])
            for body_point in [left_index, right_index, left_ankle, right_ankle]:
                universal_body_point = self.map_to_universal_point(body_point)
                self.game_path.game_evaluate_body_point(universal_body_point=universal_body_point)


    def game_update_progress_label(self, game_path: GamePath):
        if game_path:
            if self.game_path.game_mode == GAME_MODE.OBSTACLE:
                self.game_progress_callback(touched=len(game_path.touched_good_points), all=game_path.obstacle_mode_get_total_good_points_number())
            elif self.game_path.game_mode == GAME_MODE.SEQUENCE:
                self.game_progress_callback(touched=len(game_path.touched_points), all=game_path.sequence_mode_get_total_points_number())
            elif self.game_path.game_mode == GAME_MODE.ALPHABET:
                pass
                # self.update_progress_label(touched=len(game_path.player_input_alphabets), all=0)
            

    def game_show_game_points(self):
        game_mode = self.game_path.path.game_mode

        if game_mode == GAME_MODE.OBSTACLE:
            for point in self.game_path.untouched_good_points:
                camera_point = self.map_to_camera_point(point)
                cv2.circle(self.resized_image, (int(camera_point.x), int(camera_point.y)), DOT_RADIUS, GOOD_POINTS_COLOR, -1)
            for point in self.game_path.touching_good_points:
                camera_point = self.map_to_camera_point(point)
                cv2.circle(self.resized_image, (int(camera_point.x), int(camera_point.y)), DOT_RADIUS, TOUCHING_GOOD_POINTS_COLOR, -1)
            for point in self.game_path.touched_good_points:
                camera_point = self.map_to_camera_point(point)
                cv2.circle(self.resized_image, (int(camera_point.x), int(camera_point.y)), DOT_RADIUS, TOUCHED_GOOD_POINTS_COLOR, -1)

            for point in self.game_path.untouched_bad_points:
                camera_point = self.map_to_camera_point(point)
                cv2.circle(self.resized_image, (int(camera_point.x), int(camera_point.y)), DOT_RADIUS, BAD_POINTS_COLOR, -1)
            for point in self.game_path.touching_bad_points:
                camera_point = self.map_to_camera_point(point)
                cv2.circle(self.resized_image, (int(camera_point.x), int(camera_point.y)), DOT_RADIUS, TOUCHING_BAD_POINTS_COLOR, -1)
            for point in self.game_path.touched_bad_points:
                camera_point = self.map_to_camera_point(point)
                cv2.circle(self.resized_image, (int(camera_point.x), int(camera_point.y)), DOT_RADIUS, TOUCHED_BAD_POINTS_COLOR, -1)
                
        elif game_mode == GAME_MODE.SEQUENCE:
            for point in self.game_path.untouched_points:
                camera_point = self.map_to_camera_point(point)
                cv2.circle(self.resized_image, (int(camera_point.x), int(camera_point.y)), DOT_RADIUS, GOOD_POINTS_COLOR, -1)
                cv2.putText(self.resized_image, str(point.order+1), (int(camera_point.x), int(camera_point.y)), POINT_FONTFACE, POINT_FONTSCALE, POINT_TEXT_COLOR, POINT_TEXT_THICKNESS)
            for point in self.game_path.touching_points:
                camera_point = self.map_to_camera_point(point)
                cv2.circle(self.resized_image, (int(camera_point.x), int(camera_point.y)), DOT_RADIUS, TOUCHING_GOOD_POINTS_COLOR, -1)
                cv2.putText(self.resized_image, str(point.order+1), (int(camera_point.x), int(camera_point.y)), POINT_FONTFACE, POINT_FONTSCALE, POINT_TEXT_COLOR, POINT_TEXT_THICKNESS)
            for point in self.game_path.touched_points:
                camera_point = self.map_to_camera_point(point)
                cv2.circle(self.resized_image, (int(camera_point.x), int(camera_point.y)), DOT_RADIUS, TOUCHED_GOOD_POINTS_COLOR, -1)
                cv2.putText(self.resized_image, str(point.order+1), (int(camera_point.x), int(camera_point.y)), POINT_FONTFACE, POINT_FONTSCALE, POINT_TEXT_COLOR, POINT_TEXT_THICKNESS)

        elif game_mode == GAME_MODE.ALPHABET:
            for point in self.game_path.untouched_points:
                camera_point = self.map_to_camera_point(point)
                cv2.circle(self.resized_image, (int(camera_point.x), int(camera_point.y)), DOT_RADIUS, GOOD_POINTS_COLOR, -1)
            for point in self.game_path.touching_points:
                camera_point = self.map_to_camera_point(point)
                cv2.circle(self.resized_image, (int(camera_point.x), int(camera_point.y)), DOT_RADIUS, TOUCHING_GOOD_POINTS_COLOR, -1)
            for point in self.game_path.touched_points:
                camera_point = self.map_to_camera_point(point)
                cv2.circle(self.resized_image, (int(camera_point.x), int(camera_point.y)), DOT_RADIUS, TOUCHED_GOOD_POINTS_COLOR, -1)
            cv2.putText(self.resized_image, point.alphabet, (int(camera_point.x), int(camera_point.y)), POINT_FONTFACE, POINT_FONTSCALE, POINT_TEXT_COLOR, POINT_TEXT_THICKNESS)


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

    def game_finish(self):
        game_result = self.game_path.game_evaluate_result()
        return game_result


    def game_test_frame_rate(self):
        """
        Start webcam input for finding frame rate (Call Repeatedly)
        """
        if self.cap.isOpened():                
            self.camera_input_image_processing(is_test=True)

            # Send the image back to tkinter class (CameraView)
            pilImg = Image.fromarray(self.shown_image)
            imgtk = ImageTk.PhotoImage(image=pilImg)
            self.camera_view.imgtk = imgtk
            self.camera_view.configure(image=imgtk)

            # Calculate time between frames
            self.game_test_time_now = time.time_ns() // 1_000_000 # time in milliseconds
            delta = self.game_test_time_now - self.game_test_time_then # time difference between current frame and previous frame
            self.game_test_time_then = self.game_test_time_now
            self.game_test_frames.append(delta/1000)

            if len(self.game_test_frames) < GAME_TEST_FRAMES_NUMBER:
                self.camera_view.after(int(1000 / SET_CAMERA_FPS), self.game_test_frame_rate)
            else:
                self.game_test_frames.pop(0)
                average_time_between_frames = sum(self.game_test_frames) / len(self.game_test_frames)
                save_load_module = SaveLoadModule()
                sensitivity_level = save_load_module.load_settings().sensitivity_level
                self.game_path.game_load_sensitivity_level(sensitivity_level=sensitivity_level, average_time_between_frames=average_time_between_frames)                 
                self.sound_module.countdown()
                self.camera_input()


#     def map_to_spelling_point(self, point_sequence):
#         width, height = self.camera_view_width / 10, self.camera_view_height * 9 / 10
#         if self.settings.camera_orientation_mode == CAMERA_ORIENTATION.LEFT or self.settings.camera_orientation_mode == CAMERA_ORIENTATION.RIGHT:
#             width, height = height, width
#         width, height = int(width + 50*point_sequence), int(height)
#         return (width, height)


    # Methods (for SETTINGS Camera Mode)

    def settings_start(self, path:Path, change_game_mode:bool=False):
        self.camera_mode = CAMERA_MODE.SETTINGS
        self.settings_path = path
        self.settings_is_distance_calibration_shown = False
        self.universal_points_history: list[list[Point]] = [self.settings_path.points.copy()]
        self.redo_history: list[list[Point]] = []
        if not change_game_mode:
            self.camera_input()


    def settings_show_game_points(self):
        game_mode = self.settings_path.game_mode
        if game_mode == GAME_MODE.OBSTACLE:
            for point in self.settings_path.points:
                if point.is_good:
                    good_camera_point = self.map_to_camera_point(universal_point=point)
                    cv2.circle(self.resized_image, (int(good_camera_point.x), int(good_camera_point.y)), DOT_RADIUS, GOOD_POINTS_COLOR, -1)
                else:
                    bad_camera_point = self.map_to_camera_point(universal_point=point)
                    cv2.circle(self.resized_image, (int(bad_camera_point.x), int(bad_camera_point.y)), DOT_RADIUS, BAD_POINTS_COLOR, -1)

        elif game_mode == GAME_MODE.SEQUENCE:
            for point in self.settings_path.points:
                camera_point = self.map_to_camera_point(universal_point=point)
                cv2.circle(self.resized_image, (int(camera_point.x), int(camera_point.y)), DOT_RADIUS, GOOD_POINTS_COLOR, -1)
                cv2.putText(self.resized_image, str(point.order+1), (int(camera_point.x), int(camera_point.y)), POINT_FONTFACE, POINT_FONTSCALE, POINT_TEXT_COLOR, POINT_TEXT_THICKNESS)
        
        elif game_mode == GAME_MODE.ALPHABET:
            for point in self.settings_path.points:
                camera_point = self.map_to_camera_point(universal_point=point)
                cv2.circle(self.resized_image, (int(camera_point.x), int(camera_point.y)), DOT_RADIUS, GOOD_POINTS_COLOR, -1)
                cv2.putText(self.resized_image, point.alphabet, (int(camera_point.x), int(camera_point.y)), POINT_FONTFACE, POINT_FONTSCALE, POINT_TEXT_COLOR, POINT_TEXT_THICKNESS)


    def settings_update_settings(self, settings: Settings, is_distance_calibration_shown=False):
        self.settings = settings
        self.settings_is_distance_calibration_shown = is_distance_calibration_shown


    def settings_screen_pressed(self, camera_point: Point):
        new_universal_point = self.map_to_universal_point(camera_point=camera_point)
        if self.settings_path.game_mode == GAME_MODE.SEQUENCE:
            new_universal_point.order = len(self.universal_points_history[-1])
        new_universal_points = self.universal_points_history[-1] + [new_universal_point]
        self.universal_points_history.append(new_universal_points)
        self.redo_history.clear()
        self.settings_path.settings_update_points(points=new_universal_points)
        

    def settings_undo(self):
        if len(self.universal_points_history) > 1:
            old_universal_points = self.universal_points_history.pop().copy()
            new_universal_points = self.universal_points_history[-1].copy()
            self.redo_history.append(old_universal_points)
            self.settings_path.settings_update_points(points=new_universal_points)


    def settings_redo(self):
        if len(self.redo_history) > 0:
            new_universal_points = self.redo_history.pop().copy()
            self.universal_points_history.append(new_universal_points)
            self.settings_path.settings_update_points(points=new_universal_points)


    def settings_clear_all_points(self):
        universal_points = self.universal_points_history[-1].copy()
        if len(universal_points) > 0:
            new_universal_points: list[Point] = []
            self.universal_points_history.append(new_universal_points)
            self.redo_history.clear()
            self.settings_path.settings_update_points(points=new_universal_points)


    def settings_done(self) -> tuple[Path, PathImage]:
        saved_image = cv2.cvtColor(self.resized_image, cv2.COLOR_RGB2BGR)
        if self.settings.is_mirror_camera:
            saved_image = cv2.flip(saved_image, 1)

        if self.settings.camera_orientation_mode == CAMERA_ORIENTATION.LEFT:
            saved_image = cv2.rotate(saved_image, cv2.ROTATE_90_CLOCKWISE)
        elif self.settings.camera_orientation_mode == CAMERA_ORIENTATION.RIGHT:
            saved_image = cv2.rotate(saved_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif self.settings.camera_orientation_mode == CAMERA_ORIENTATION.INVERTED:
            saved_image = cv2.rotate(saved_image, cv2.ROTATE_180)

        path_image = PathImage(path_id=self.settings_path.id, image=saved_image)
        return self.settings_path, path_image


    # Debug Methods (for GAME Camera Mode)

    def game_simulate_body_point(self, camera_point:Point=None):
        if camera_point:
            self.debug_game_camera_point = camera_point
        else:
            self.debug_game_camera_point = None
