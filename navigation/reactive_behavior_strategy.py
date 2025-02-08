from robot_navigation.navigation.navigation_strategy import NavigationStrategy

# Define critical thresholds.
SAFE_DISTANCE = 0.15  # Base safe distance (meters)
MARGIN = 0.05         # Additional margin (meters)

class ReactiveBehaviorStrategy(NavigationStrategy):

    def decide(self, detections: list) -> tuple[float, float]:
        # Default: drive forward.
        left_cmd = 0.0
        right_cmd = 0.0

        if not detections:
            print("[DEBUG] No detections. Driving forward.")
            return left_cmd, right_cmd

        # Assume all detections share the same camera dimensions.
        camera_width = detections[0].get("camera_width", 1280)
        left_boundary = camera_width / 3
        right_boundary = 2 * camera_width / 3
        print(f"[DEBUG] Camera width: {camera_width}, Left boundary: {left_boundary}, Right boundary: {right_boundary}")

        # Initialize minimum distance values for each segment.
        left_min = float('inf')
        center_min = float('inf')
        right_min = float('inf')

        for det in detections:
            distance = det.get("distance", float('inf'))
            bbox = det.get("bbox", [0, 0, 0, 0])
            center_x = (bbox[0] + bbox[2]) / 2.0
            label = det.get("label", "unknown")
            print(f"[DEBUG] Detection '{label}': center_x = {center_x:.1f}, distance = {distance:.3f}")

            if center_x < left_boundary:
                left_min = min(left_min, distance)
                print(f"   [DEBUG] -> Assigned to LEFT; updated left_min = {left_min:.3f}")
            elif center_x > right_boundary:
                right_min = min(right_min, distance)
                print(f"   [DEBUG] -> Assigned to RIGHT; updated right_min = {right_min:.3f}")
            else:
                center_min = min(center_min, distance)
                print(f"   [DEBUG] -> Assigned to CENTER; updated center_min = {center_min:.3f}")

        print(f"[DEBUG] Minimum distances -> Left: {left_min:.3f}, Center: {center_min:.3f}, Right: {right_min:.3f}")

        # Navigation decision logic:
        # 1. If an obstacle in the center is dangerously close, turn in place.
        if center_min < SAFE_DISTANCE:
            print(f"[DEBUG] Center obstacle too close (center_min = {center_min:.3f} < SAFE_DISTANCE = {SAFE_DISTANCE}).")
            # Steer away from the side that is also close.
            if left_min > right_min:
                left_cmd, right_cmd = 1.0, -1.0  # Turn right.
                print("[DEBUG] Turning right (left side is safer).")
            else:
                left_cmd, right_cmd = -1.0, 1.0  # Turn left.
                print("[DEBUG] Turning left (right side is safer).")
        else:
            # 2. If the center is free but one or both sides are borderline,
            # steer away from the closer wall.
            if left_min < (SAFE_DISTANCE + MARGIN) or right_min < (SAFE_DISTANCE + MARGIN):
                if left_min < right_min:
                    # Left side is closer (more dangerous).
                    left_cmd, right_cmd = 1.0, 0.7  # Steer right.
                    print(f"[DEBUG] Left side too close (left_min = {left_min:.3f}). Steering right.")
                elif right_min < left_min:
                    # Right side is closer.
                    left_cmd, right_cmd = 0.7, 1.0  # Steer left.
                    print(f"[DEBUG] Right side too close (right_min = {right_min:.3f}). Steering left.")
                else:
                    # If both are nearly the same, pick a mild steering.
                    left_cmd, right_cmd = 0.9, 1.0
                    print("[DEBUG] Both sides are borderline. Slight adjustment.")
            else:
                # 3. If all segments are clear beyond the margin, drive forward.
                left_cmd, right_cmd = 1.0, 1.0
                print("[DEBUG] All segments clear. Driving forward.")

        print(f"[DEBUG] Final command: left_cmd = {left_cmd}, right_cmd = {right_cmd}")
        return left_cmd, right_cmd
