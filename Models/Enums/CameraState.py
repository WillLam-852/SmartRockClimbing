from enum import Enum

class CAMERA_STATE(Enum):
    UNAVAILABLE = -1
    PLAYING = 0
    PAUSE = 1
    RECORDING = 2