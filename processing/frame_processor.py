from robot_navigation.data.sensor_data import SensorData

class FrameProcessor:
    def __init__(self, detector, tracker, visualizer):
        self.detector = detector  # e.g., an instance of YOLOv11Detector
        self.tracker = tracker    # e.g., an instance of StereoTracker
        self.visualizer = visualizer # e.g. an instance of FrameVisualizer

    def process(self, left_frame, right_frame) -> SensorData:
        # Run detection on each frame.
        left_detections = self.detector.detect(left_frame)
        right_detections = self.detector.detect(right_frame)
        
        # Update the tracker with the detections.
        tracking_objects = self.tracker.update(left_detections, right_detections)

        left_frame_visualized = self.visualizer.draw_enriched_frame(left_frame.copy(), left_detections)
        right_frame_visualized = self.visualizer.draw_enriched_frame(right_frame.copy(), right_detections)

        # Create and return a SensorData object.
        return SensorData(
            left_frame=left_frame,
            right_frame=right_frame,
            left_frame_visualized=left_frame_visualized,
            right_frame_visualized=right_frame_visualized,
            left_detections=left_detections,
            right_detections=right_detections,
            tracking_objects=tracking_objects
        )
