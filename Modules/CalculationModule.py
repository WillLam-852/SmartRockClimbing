import cv2
import numpy as np

from Models.Calculation.CalculationResultWithImage import CalculationResultWithImage
from Models.Path import Point
from Modules.SaveLoadModule import SaveLoadModule
from Utilities.Constants import *

class CalculationModule:
    """
    A module used in PoseDetectionModule, to calculate angle and distance

    Attributes
    ----------
    image_without_drawing : ndarray
        original pause image
    image_with_drawing : ndarray
        pause image for adding point and line on it
    distance_calibration_actual_value : float
        Actual distance (in metre) of the calibrated 'yellow line'
    clickedPoints : Point
        A list of points user clicked on screen (min: 0, max: 3)
    dot_color : tuple[int]
        RGB value of dot color
    angle_color : tuple[int]
        RGB value of angle color
    """
    
    def __init__(self, image: np.ndarray=None, is_video_player:bool=False):
        if image is not None:
            self.image_without_drawing = image.copy()
            self.image_with_drawing = image.copy()
        self.distance_calibration_actual_value = SaveLoadModule().load_settings().distance_calibration_actual_value
        self.clickedPoints: list[Point] = []
        if is_video_player:
            self.dot_color = (DOT_COLOR[2], DOT_COLOR[1], DOT_COLOR[0])
            self.angle_color = (ANGLE_COLOR[2], ANGLE_COLOR[1], ANGLE_COLOR[0])
        else:
            self.dot_color = DOT_COLOR
            self.angle_color = ANGLE_COLOR


    def find_angle_between_three_points(self, pt1: Point, pt2: Point, pt3: Point) -> np.float64:
        a = np.array([pt1.x, pt1.y])
        b = np.array([pt2.x, pt2.y])
        c = np.array([pt3.x, pt3.y])
        ba = a - b
        bc = c - b
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle)
        return np.degrees(angle)


    def find_angle_between_lines_and_x_axis(self, pt1: Point, pt2: Point) -> np.float64:
        a = np.array([pt1.x, pt1.y])
        b = np.array([pt2.x, pt2.y])
        c = np.array([10000, pt2.y])
        ba = a - b
        bc = c - b
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle)
        if pt1.y < pt2.y:
            angle = -angle
        if angle < 0:
            angle = angle + np.pi * 2
        return np.degrees(angle)


    def find_distance_between_two_points(self, pt1: Point, pt2: Point) -> float:
        self.pixels_on_screen = np.sqrt(np.square(pt1.x-pt2.x) + np.square(pt1.y-pt2.y))
        self.distance_factor = self.distance_calibration_actual_value / CALIBRATION_PIXELS
        self.distance = self.pixels_on_screen * self.distance_factor
        return self.distance


    def drawAngle(self):
        fromAngle = self.find_angle_between_lines_and_x_axis(self.clickedPoints[0], self.clickedPoints[1])
        toAngle = self.find_angle_between_lines_and_x_axis(self.clickedPoints[2], self.clickedPoints[1])
        if abs(toAngle-fromAngle) > 180:
            if toAngle > fromAngle:
                toAngle -= 360
            else:
                fromAngle -= 360
        cv2.ellipse(self.image_with_drawing, (self.clickedPoints[1].x, self.clickedPoints[1].y), (DOT_RADIUS*4, DOT_RADIUS*4), 0, fromAngle, toAngle, self.angle_color, -1)


    def calculate(self, point: Point) -> CalculationResultWithImage:
        angle: float = None
        distance: float = None
        self.clickedPoints.append(point)
        cv2.circle(self.image_with_drawing, (point.x, point.y), DOT_RADIUS, self.dot_color, -1)
        if len(self.clickedPoints) == 2:
            cv2.line(self.image_with_drawing, (self.clickedPoints[0].x, self.clickedPoints[0].y), (self.clickedPoints[1].x, self.clickedPoints[1].y), self.dot_color, int(DOT_RADIUS/3))
            distance = self.find_distance_between_two_points(self.clickedPoints[0], self.clickedPoints[1])
        if len(self.clickedPoints) == 3:
            cv2.line(self.image_with_drawing,  (self.clickedPoints[1].x, self.clickedPoints[1].y),  (self.clickedPoints[2].x, self.clickedPoints[2].y), self.dot_color, int(DOT_RADIUS/3))
            angle = self.find_angle_between_three_points(self.clickedPoints[0], self.clickedPoints[1], self.clickedPoints[2])
            self.drawAngle()
        if len(self.clickedPoints) > 3:
            self.clear_all_dots()
        calculation_result_with_image = CalculationResultWithImage(image_with_drawing=self.image_with_drawing, distance=distance, angle=angle)
        return calculation_result_with_image


    def clear_all_dots(self):
        self.clickedPoints.clear()
        self.image_with_drawing = self.image_without_drawing.copy()
        return self.image_with_drawing
