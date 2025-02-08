from robot_navigation.navigation.navigation_strategy import NavigationStrategy

class PotentialFieldStrategy(NavigationStrategy):
    def decide(self, detections: list) -> tuple[float, float]:
        # TODO: Implement potential field logic.
        return 1.0, 1.0