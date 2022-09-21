from Models.Enums.GameMode import GAME_MODE
from Models.Path.Path import Path
from Models.Path.Point import Point
from Models.SavedData.SavedRow import SavedRow

class PathInGame:
    """
    A class representing each path during game

    Attributes
    ----------
    id : str
    name : str
    game_mode : GAME_MODE
        OBSTACLE, SEQUENCE or ALPHABET
    points: list[SavedPoint]
        a list of saved points of this path
    """

    def __init__(self, path: Path):
        self.path = path


    def toSavedRows(self) -> list[SavedRow]:
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