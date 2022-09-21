import numpy as np

class PathImage:
    """
    Path Image to be saved in storage

    Attributes
    ----------
    path_id : str
        corresponding path id of this image
    image : np.ndarray
        thge path image with game dots on it
    """

    def __init__(self, path_id: str, image: np.ndarray):
        self.path_id = path_id
        self.image = image
