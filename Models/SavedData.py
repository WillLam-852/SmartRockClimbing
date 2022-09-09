from typing import List
from Models.Enums.GameMode import GAME_MODE

# Represent each row in .csv file
class SavedData:
    def __init__(self, path_id: str, path_name: str, path_gamemode: GAME_MODE, point_x: int, point_y: int, point_is_good:bool, point_order:int, point_alphabet:str):
        self.path_id = path_id
        self.path_name = path_name
        self.path_gamemode = path_gamemode
        self.point_x = point_x
        self.point_y = point_y
        self.point_is_good = point_is_good
        self.point_order = point_order
        self.point_alphabet = point_alphabet


class SavedPoint:
    # is_good: In Obstacle Mode, is_good==True are the points player needs to touch. is_good==False are the points player needs to avoid.
    # order: In Sequence Mode, order is the order of points player needs to follow.
    # alphabet: In Alphabet Mode, alphabet is the alphabet this point represent.
    def __init__(self, x: int, y: int, is_good:bool=True, order:int=0, alphabet:str=''):
        self.x = x
        self.y = y
        self.is_good = is_good
        self.order = order
        self.alphabet = alphabet        


class SavedPath:
    def __init__(self, id: str, name: str, gamemode: GAME_MODE):
        self.id = id
        self.name = name
        self.game_mode = gamemode

    def createSavedFile(self, savedPoints: List[SavedPoint]) -> List[SavedData]:
        savedFile: List[SavedData] = []
        for savedPoint in savedPoints:
            savedData = SavedData(
                path_id=self.id,
                path_name=self.name,
                path_gamemode=self.game_mode,
                point_x=savedPoint.x,
                point_y=savedPoint.y,
                point_is_good=savedPoint.is_good,
                point_order=savedPoint.order,
                point_alphabet=savedPoint.alphabet
            )
            savedFile.append(savedData)
        return savedFile