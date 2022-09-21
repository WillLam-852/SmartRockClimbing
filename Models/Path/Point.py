class Point:
    """
    A class representing each point

    Attributes
    ----------
    x : int
    y : int
    is_good : bool (Used in OBSTACLE Game Mode)
        is_good==True are the points player needs to touch. is_good==False are the points player needs to avoid.
    order: int (Used in SEQUENCE Game Mode)
        the order of points player needs to follow to touch
    alphabet: str (Used in ALPHABET Game Mode)
        the alphabet this point represents.
    """
    def __init__(self, x: int, y: int, is_good:bool=True, order:int=0, alphabet:str=''):
        self.x = x
        self.y = y
        self.is_good = is_good
        self.order = order
        self.alphabet = alphabet        