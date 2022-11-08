from __future__ import annotations
import cv2
from Models.Enums.GameMode import GAME_MODE
from Models.Path.Path import Path
from Models.Path.Point import Point
from Utilities.Constants import *
from Utilities.OpenFile import open_file

class GameResult:
    def __init__(self, path: Path, touched_good_points: list[Point], untouched_good_points: list[Point], touched_bad_points: list[Point], untouched_bad_points: list[Point], alphabets: list[str]):
        self.path = path
        self.touched_good_points: list[Point] = touched_good_points
        self.untouched_good_points: list[Point] = untouched_good_points
        self.touched_bad_points: list[Point] = touched_bad_points
        self.untouched_bad_points: list[Point] = untouched_bad_points
        self.alphabets: list[str] = alphabets
        self.evaluate(game_mode=path.game_mode)


    def evaluate(self, game_mode: GAME_MODE):
        if game_mode == GAME_MODE.OBSTACLE:
            add_scores: int = len(self.touched_good_points) * TOUCHED_GOOD_POINT_WEIGHT
            minus_scores: int = len(self.touched_bad_points) * TOUCHED_BAD_POINT_WEIGHT
            self.score = add_scores - minus_scores
        elif game_mode == GAME_MODE.SEQUENCE:
            add_scores: int = len(self.touched_good_points) * TOUCHED_GOOD_POINT_WEIGHT
            self.score = add_scores
        

    def update_time(self, time):
        self.time = time


    def get_score(self) -> int:
        """
        Get the score this player gets
        """
        return self.score


    def get_full_score(self) -> int:
        """
        Get the total score of this path
        """
        full_score = TOUCHED_GOOD_POINT_WEIGHT * (len(self.touched_good_points)+len(self.untouched_good_points))
        return full_score


    def get_good_points_number(self) -> tuple[int, int]:
        """
        Get the number of touched good points, and the number of total good points
        """
        return len(self.touched_good_points), len(self.touched_good_points)+len(self.untouched_good_points)


    def get_bad_points_number(self) -> tuple[int, int]:
        """
        Get the number of touched bad points, and the number of total bad points
        """
        return len(self.touched_bad_points), len(self.touched_bad_points)+len(self.untouched_bad_points)


    def get_points_lists(self) -> tuple[list[Point], list[Point], list[Point], list[Point]]:
        """
        Get the lists of touched_good_points, untouched_good_points, touched_bad_points, and untouched_bad_points
        """
        return self.touched_good_points, self.untouched_good_points, self.touched_bad_points, self.untouched_bad_points


    # def get_word(self):
    #     word = ''.join(str(alphabets[1][4]) for alphabets in self.alphabet_list)
    #     return word


    def get_time(self):
        return self.time


    def get_image(self):
        self.image = cv2.imread(open_file(f"{PATH_IMAGE_FILE_LOCATION}{CURRENT_PATH_SET}_{self.path.id}.jpg"), -1)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        return self.image