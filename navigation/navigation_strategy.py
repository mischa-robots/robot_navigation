from abc import ABC, abstractmethod

class NavigationStrategy(ABC):
    @abstractmethod
    def decide(self, detections: list) -> tuple[float, float]:
        """
        Given a list of detection dicts, return (left_speed, right_speed).
        Speeds are values in [-1.0, 1.0].
        """
        pass
