from time import sleep
from robot_navigation.navigation.navigation_strategy import NavigationStrategy
from robot_navigation.data.sensor_data import SensorData

# Define critical thresholds.
SAFE_DISTANCE = 0.15  # Base safe distance (meters)

class ReactiveBehaviorStrategy(NavigationStrategy):

    def decide(self, sensor_data: SensorData) -> tuple[float, float]:
        # Default: stop the robot when no detections available or no decision can be made:
        left_cmd = 0.0
        right_cmd = 0.0

        print("[DEBUG] ReactiveBehaviorStrategy got sensor data:", flush=True)

        print(f"sensor_data.left_detections", flush=True)
        print(f"{sensor_data.left_detections}", flush=True)

        print(f"sensor_data.right_detections", flush=True)
        print(f"{sensor_data.right_detections}", flush=True)

        print(f"sensor_data.tracking_objects", flush=True)
        print(f"{sensor_data.tracking_objects}", flush=True)

        sleep(10)

        return left_cmd, right_cmd
