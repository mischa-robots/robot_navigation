from robot_navigation.navigation.navigation_strategy import NavigationStrategy

class ReinforcementLearningStrategy(NavigationStrategy):
    def decide(self, detections: list) -> tuple[float, float]:
        # TODO: Use a trained RL model to decide.
        return 1.0, 1.0