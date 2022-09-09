from Models.Enums.CameraOrientation import CAMERA_ORIENTATION
from Models.Enums.SensitivityLevel import SENSITIVITY_LEVEL
from Utilities.Constants import *

class Settings:

    # Default Settings
    def __init__(self):
        self.camera_number = 0
        self.camera_orientation_mode = CAMERA_ORIENTATION.LANDSCAPE
        self.is_danger_alert_on = True
        self.is_mirror_camera = False
        self.is_reverse_keypad = False
        self.distance_calibration_actual_value = 1.0
        self.ground_ratio_calibration_actual_value = 0.8
        self.sensitivity_level = SENSITIVITY_LEVEL.MIDDLE


    def update(
            self, 
            camera_number:int=None, 
            camera_orientation_mode:CAMERA_ORIENTATION=None, 
            is_danger_alert_on:bool=None, 
            is_mirror_camera:bool=None, 
            is_reverse_keypad:bool=None, 
            distance_calibration_actual_value:float=None, 
            ground_ratio_calibration_actual_value:float=None, 
            sensitivity_level:SENSITIVITY_LEVEL=None
        ):
        if camera_number:
            self.camera_number = camera_number
        if camera_orientation_mode:
            self.camera_orientation_mode = camera_orientation_mode
        if is_danger_alert_on:
            self.is_danger_alert_on = is_danger_alert_on
        if is_mirror_camera:
            self.is_mirror_camera = is_mirror_camera
        if is_reverse_keypad:
            self.is_reverse_keypad = is_reverse_keypad
        if distance_calibration_actual_value:
            self.distance_calibration_actual_value = distance_calibration_actual_value
        if ground_ratio_calibration_actual_value:
            self.ground_ratio_calibration_actual_value = ground_ratio_calibration_actual_value
        if sensitivity_level:
            self.sensitivity_level = sensitivity_level


    def convert_to_variables(self):
        variables = {
            CAMERA_NUMBER: self.camera_number,
            CAMERA_ORIENTATION_MODE: self.camera_orientation_mode,
            IS_DANGER_ALERT_ON: self.is_danger_alert_on,
            IS_MIRROR_CAMERA: self.is_mirror_camera,
            IS_REVERSE_KEYPAD: self.is_reverse_keypad,
            DISTANCE_CALIBRATION_ACTUAL_VALUE: self.distance_calibration_actual_value,
            GROUND_RATIO_CALIBRATION_ACTUAL_VALUE: self.ground_ratio_calibration_actual_value,
            SENSITIVITY: self.sensitivity_level
        }
        return variables
    
    
    def convert_from(self, variables):
        self.update(
            camera_number=variables[CAMERA_NUMBER],
            camera_orientation_mode=variables[CAMERA_ORIENTATION_MODE],
            is_danger_alert_on=variables[IS_DANGER_ALERT_ON],
            is_mirror_camera=variables[IS_MIRROR_CAMERA],
            is_reverse_keypad=variables[IS_REVERSE_KEYPAD],
            distance_calibration_actual_value=variables[DISTANCE_CALIBRATION_ACTUAL_VALUE],
            ground_ratio_calibration_actual_value=variables[GROUND_RATIO_CALIBRATION_ACTUAL_VALUE],
            sensitivity_level=variables[SENSITIVITY]
        )
