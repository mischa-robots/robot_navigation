from robot_navigation.data.sensor_data import SensorData

class FrameProcessor:
    def __init__(self, sensor_data_hub, detector, tracker, visualizer):
        self.sensor_data_hub = sensor_data_hub
        self.detector = detector      # e.g., an instance of YoloDetector
        self.tracker = tracker        # e.g., an instance of StereoTracker
        self.visualizer = visualizer  # e.g., an instance of FrameVisualizer

    def process_and_update(self, left_frame, right_frame) -> SensorData:

        # Run detection on each frame.
        left_detections = self.detector.detect(left_frame)
        right_detections = self.detector.detect(right_frame)

        # Update the tracker with the detections.
        tracking_objects = self.tracker.update(left_detections, right_detections)

        # Generate enriched (annotated) frames.
        left_frame_visualized = self.visualizer.draw_enriched_frame(left_frame.copy(), left_detections)
        right_frame_visualized = self.visualizer.draw_enriched_frame(right_frame.copy(), right_detections)

        # Package everything into a SensorData object.
        sensor_data = SensorData(
            left_frame=left_frame,
            right_frame=right_frame,
            left_frame_visualized=left_frame_visualized,
            right_frame_visualized=right_frame_visualized,
            left_detections=left_detections,
            right_detections=right_detections,
            tracking_objects=tracking_objects
        )
        # Update the shared hub.
        self.sensor_data_hub.update(sensor_data)
        return sensor_data
