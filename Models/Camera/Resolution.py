from turtle import width


class Resolution:

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

    def exchange_width_height(self) -> None:
        self.width, self.height = self.height, self.width