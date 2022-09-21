from Models.Enums.GameMode import GAME_MODE
from Models.Path.Point import Point
from Models.SavedData.SavedRow import SavedRow

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
        if game_mode == GAME_MODE.OBSTACLE:
            self.obstacle_mode_create_points_list(points=points)


    def update_points(self, points: list[Point]):
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


    def obstacle_mode_create_points_list(self, points: list[Point]):
        """
        Create 2 points lists for good points and bad points (Used in OBSTACLE MODE only)
        
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