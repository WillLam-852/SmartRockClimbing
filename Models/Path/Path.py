from __future__ import annotations
from Models.Enums.GameMode import GAME_MODE
from Models.Path.Point import Point
from Models.SavedData.SavedRow import SavedRow
from Utilities.Constants import *

class Path:
    """
    A class representing each path

    Attributes
    ----------
    id : str
    created_timestamp : float
    name : str
    game_mode : GAME_MODE
        OBSTACLE, SEQUENCE or ALPHABET
    points: list[Point]
        a list of (universal) points of this path
    """

    def __init__(self, id: str, created_timestamp: float, name: str, game_mode: GAME_MODE, points: list[Point]):
        self.id = id
        self.created_timestamp = created_timestamp
        self.name = name
        self.game_mode = game_mode
        self.points = points


    def settings_update_points(self, points: list[Point]):
        """
        Overwrite the points of this path (Used in SETTINGS Camera Mode)
        
        Parameters
        ----------
        points: list[Point]
            Points that overwritten in Path
        """
        self.points = points


    def settings_obstacle_is_any_good_points(self) -> bool:
        """
        Check if any good points in Settings Done (Used in OBSTACLE Game Mode only)
        """
        for point in self.points:
            if point.is_good:
                return True
        return False


    def to_saved_rows(self) -> list[SavedRow]:
        """
        Create a list of SavedRows for this path to be saved in .csv file
        """
        savedFile: list[SavedRow] = []
        for savedPoint in self.points:
            savedData = SavedRow(
                path_id=self.id,
                path_created_timestamp=self.created_timestamp,
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