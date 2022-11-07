import numpy as np

from Models.Enums.GameMode import GAME_MODE
from Models.Enums.SensitivityLevel import SENSITIVITY_LEVEL
from Models.Path.GameResult import GameResult
from Models.Path.Path import Path
from Models.Path.Point import Point
from Modules.SoundModule import SoundModule
from Utilities.Constants import *

class GamePath:
    """
    A class representing each path during Game

    Attributes
    ----------
    path: Path
        corresponding path
    """

    def __init__(self, path: Path):
        self.path = path
        self.points = path.points
        self.untouched_points: list[Point] = self.points
        self.touching_points: list[Point] = []
        self.touched_points: list[Point] = []
        self.sound_module = SoundModule()
        self.game_mode = path.game_mode
        if self.game_mode == GAME_MODE.OBSTACLE:
            self.obstacle_mode_create_good_bad_points_list()
        elif self.game_mode == GAME_MODE.SEQUENCE:
            self.sequence_current_order = 0
        elif self.game_mode == GAME_MODE.ALPHABET:
            self.alphabet_player_input_alphabets: list[str] = []


    def obstacle_mode_create_good_bad_points_list(self):
        """
        Seperate points lists into good points list and bad points list (Used in OBSTACLE Game Mode only)
        """
        untouched_good_points: list[Point] = []
        untouched_bad_points: list[Point] = []
        for point in self.untouched_points:
            if point.is_good:
                untouched_good_points.append(point)
            else:
                untouched_bad_points.append(point)
        self.untouched_good_points = untouched_good_points
        self.untouched_bad_points = untouched_bad_points
        self.touching_good_points: list[Point] = []
        self.touching_bad_points: list[Point] = []
        self.touched_good_points: list[Point] = []
        self.touched_bad_points: list[Point] = []


    def obstacle_mode_get_all_good_points_number(self) -> int:
        """
        Get the good points list (for showing the total number in progress label)
        """
        good_points: list[Point] = self.untouched_good_points + self.touched_good_points
        return len(good_points)


    def game_load_sensitivity_level(self, sensitivity_level: SENSITIVITY_LEVEL, average_time_between_frames: float):
        """
        Load sensitivity level from settings and calculate count parameters (Used in GAME Camera Mode only)
        
        Parameters
        ----------
        average_time_between_frames: float
        """
        if sensitivity_level == SENSITIVITY_LEVEL.VERY_LOW:
            self.touch_distance = 0.01
            self.count_second = 4
        elif sensitivity_level == SENSITIVITY_LEVEL.LOW:
            self.touch_distance = 0.02
            self.count_second = 3.5
        elif sensitivity_level == SENSITIVITY_LEVEL.MEDIUM:
            self.touch_distance = 0.03
            self.count_second = 3
        elif sensitivity_level == SENSITIVITY_LEVEL.HIGH:
            self.touch_distance = 0.04
            self.count_second = 2.5
        elif sensitivity_level == SENSITIVITY_LEVEL.VERY_HIGH:
            self.touch_distance = 0.05
            self.count_second = 2
        self.count_threshold = int(self.count_second / average_time_between_frames)
        if DEBUG_MODE:
            print("----------------- game_load_sensitivity ---------------")
            print("average_time_between_frames:", average_time_between_frames)
            print("count_threshold:", self.count_threshold)
            print("count_second:", self.count_second)
            print("touch_distance_pixel:", self.touch_distance)
            print()


    def game_evaluate_body_point(self, universal_body_point: Point):
        if self.path.game_mode == GAME_MODE.OBSTACLE:
            for point in self.untouched_good_points:
                if self.distance_between(universal_body_point, point) < self.touch_distance:
                    # Append this point (with duplicates)
                    self.touching_good_points.append(point)
                    # If this point exceed count_threshold in touching_list, add this point to touched_list (without duplicates)
                    if self.touching_good_points.count(point) > self.count_threshold:
                        self.untouched_good_points.remove(point)
                        self.touching_good_points = list(filter((point).__ne__, self.touching_good_points))
                        self.touched_good_points.append(point)
                        self.sound_module.good_point()
            for point in self.untouched_bad_points:
                if self.distance_between(universal_body_point, point) < self.touch_distance:
                    # Append this point (with duplicates)
                    self.touching_bad_points.append(point)
                    # If this point exceed count_threshold in touching_list, add this point to touched_list (without duplicates)
                    if self.touching_bad_points.count(point) > self.count_threshold:
                        self.untouched_bad_points.remove(point)
                        self.touching_bad_points = list(filter((point).__ne__, self.touching_bad_points))
                        self.touched_bad_points.append(point)
                        self.sound_module.bad_point()

        elif self.path.game_mode == GAME_MODE.SEQUENCE:
            for point in self.untouched_points:
                if point.order == self.sequence_current_order and self.distance_between(universal_body_point, point) < self.touch_distance:
                    # Append this point (with duplicates)
                    self.touching_points.append(point)
                    # If this point exceed count_threshold in touching_list, add this point to touched_list (without duplicates)
                    if self.touching_points.count(point) > self.count_threshold:
                        self.untouched_points.remove(point)
                        self.touching_points = list(filter((point).__ne__, self.touching_good_points))
                        self.touched_points.append(point)
                        self.sound_module.good_point()
                        self.sequence_current_order += 1

        elif self.path.game_mode == GAME_MODE.ALPHABET:
            for point in self.points:
                if self.distance_between(universal_body_point, point) < self.touch_distance:
                    # Append this point (with duplicates)
                    self.touching_points.append(point)
                    # If this point exceed count_threshold in touching_list, add this point to touched_list (without duplicates)
                    if self.touching_points.count(point) > self.count_threshold:
                        self.untouched_points.remove(point)
                        self.touching_points = list(filter((point).__ne__, self.touching_good_points))
                        self.touched_points.append(point)
                        self.sound_module.good_point()
                        self.alphabet_player_input_alphabets.append(point.alphabet)


    def game_evaluate_result(self):
        result = GameResult(self.path)
        return result


    def distance_between(self, pt1: Point, pt2: Point) -> float:
        return np.sqrt(np.square(pt1.x-pt2.x) + np.square(pt1.y-pt2.y))