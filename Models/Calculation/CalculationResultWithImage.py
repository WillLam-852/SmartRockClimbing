from Models.Calculation.CalculationResult import CalculationResult

class CalculationResultWithImage:

    def __init__(self, image_with_drawing, distance: float, angle: float):
        self.image_with_drawing = image_with_drawing
        self.calculation_result = CalculationResult(distance=distance, angle=angle)
