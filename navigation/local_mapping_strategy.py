from robot_navigation.navigation.navigation_strategy import NavigationStrategy

class LocalMappingStrategy(NavigationStrategy):
    def decide(self, detections: list) -> tuple[float, float]:
        # TODO: Implement local mapping and lightweight planning.
        return 1.0, 1.0