# Improved Position Mapper - Generated from Calibration Analysis
# This code can be used to replace the position_to_choice method


def improved_position_to_choice(self, question_num: int, position: List[int]) -> str:
    """
    Improved position to choice mapping based on calibration analysis
    Calibrated on: 5 detected boundaries
    X range: [np.float64(73.0), np.float64(1929.0)]
    """
    x, y = position
    
    # Calibrated boundaries for choices A, B, C, D, E
    boundaries = [np.float64(258.6), np.float64(629.8), np.float64(1001.0), np.float64(1372.2), np.float64(1743.3999999999999)]
    choices = ["A", "B", "C", "D", "E"]
    
    # Find the appropriate choice based on X coordinate
    for i, boundary in enumerate(boundaries):
        if x < boundary:
            return choices[i]
    
    # If X is greater than all boundaries, return E
    return "E"
