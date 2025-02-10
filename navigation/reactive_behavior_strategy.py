from robot_navigation.navigation.navigation_strategy import NavigationStrategy
from robot_navigation.data.sensor_data import SensorData

# Define critical thresholds.
SAFE_DISTANCE = 0.15  # Base safe distance (meters)

class ReactiveBehaviorStrategy(NavigationStrategy):

    def decide(self, sensor_data: SensorData) -> tuple[float, float]:
        # Default: stop the robot when no detections available or no decision can be made:
        left_cmd = 0.0
        right_cmd = 0.0

        return left_cmd, right_cmd
