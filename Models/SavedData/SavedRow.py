from Models.Enums.GameMode import GAME_MODE

class SavedRow:
    """
    A class representing each row in .csv file

    Attributes
    ----------
    path_id : str
    path_name : str
    path_game_mode : GAME_MODE
    point_x : int
    point_y : int
    point_is_good : bool (Used in OBSTACLE Game Mode)
        is_good==True are the points player needs to touch. is_good==False are the points player needs to avoid.
    point_order: int (Used in SEQUENCE Game Mode)
        the order of points player needs to follow to touch
    point_alphabet: str (Used in ALPHABET Game Mode)
        the alphabet this point represents.
    """
    
    def __init__(self, path_id: str, path_name: str, path_game_mode: GAME_MODE, point_x: int, point_y: int, point_is_good:bool, point_order:int, point_alphabet:str):
        self.path_id = path_id
        self.path_name = path_name
        self.path_game_mode = path_game_mode
        self.point_x = point_x
        self.point_y = point_y
        self.point_is_good = point_is_good
        self.point_order = point_order
        self.point_alphabet = point_alphabet