from Models.Enums.GameMode import GAME_MODE
from Models.Enums.SensitivityLevel import SENSITIVITY_LEVEL
from Models.Path.Point import Point
from Models.SavedData.SavedRow import SavedRow
from Modules.SaveLoadModule import SaveLoadModule
from Utilities.Constants import *

class Path:
    """
    A class representing each path

    Attributes
    ----------
    id : str
    name : str
    game_mode : GAME_MODE
        OBSTACLE, SEQUENCE or ALPHABET
    points: list[Point]
        a list of (universal) points of this path
    """

    def __init__(self, id: str, name: str, game_mode: GAME_MODE, points: list[Point]):
        self.id = id
        self.name = name
        self.game_mode = game_mode
        self.points = points
        self.save_load_module = SaveLoadModule()
        if game_mode == GAME_MODE.OBSTACLE:
            self.obstacle_mode_create_points_list(points=points)


    def obstacle_mode_create_points_list(self, points: list[Point]):
        """
        Create 2 points lists for good points and bad points (Used in OBSTACLE Game Mode only)
        
        Parameters
        ----------
        points: list[Point]
            Points to be divided into 2 lists
        """
        good_points: list[Point] = []
        bad_points: list[Point] = []
        for point in points:
            if point.is_good:
                good_points.append(point)
            else:
                bad_points.append(point)
        self.good_points = good_points
        self.bad_points = bad_points


    def game_load_sensitivity_level(self, average_time_between_frames: float):
        """
        Load sensitivity level from settings and calculate count parameters (Used in GAME Camera Mode only)
        
        Parameters
        ----------
        average_time_between_frames: float
        """
        sensitivity_level = self.save_load_module.load_settings().sensitivity_level
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


    def settings_update_points(self, points: list[Point]):
        """
        Overwrite the points of this path (Used in SETTINGS Camera Mode)
        
        Parameters
        ----------
        points: list[Point]
            Points that overwritten in Path
        """
        self.points = points
        if self.game_mode == GAME_MODE.OBSTACLE:
            self.obstacle_mode_create_points_list(points=points)


    def to_saved_rows(self) -> list[SavedRow]:
        """
        Create a list of SavedRows for this path to be saved in .csv file
        """
        savedFile: list[SavedRow] = []
        for savedPoint in self.points:
            savedData = SavedRow(
                path_id=self.id,
                path_name=self.name,
                path_game_mode=self.game_mode,
                point_x=savedPoint.x,
                point_y=savedPoint.y,
                point_is_good=savedPoint.is_good,
                point_order=savedPoint.order,
                point_alphabet=savedPoint.alphabet
            )
            savedFile.append(savedData)
        return savedFile