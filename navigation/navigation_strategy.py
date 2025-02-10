from abc import ABC, abstractmethod
from robot_navigation.data.sensor_data import SensorData

class NavigationStrategy(ABC):
    @abstractmethod
    def decide(self, sensor_data: SensorData) -> tuple[float, float]:
        """
        Given sensor data (which may include frames, detections, tracking data, etc.),
        return a tuple (left_speed, right_speed) with speeds in [-1.0, 1.0].
        """
        pass
