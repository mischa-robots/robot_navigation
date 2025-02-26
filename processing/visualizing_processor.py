from robot_navigation.processing.processing_module import ProcessingModule
from robot_navigation.data.sensor_data import SensorData
from robot_navigation.visualizing.frame_visualizer import FrameVisualizer

class VisualizingProcessor(ProcessingModule):
    def __init__(self, visualizer: FrameVisualizer):
        self.visualizer = visualizer

    def process(self, sensor_data: SensorData):
        sensor_data.left_frame_visualized = self.visualizer.draw_enriched_frame(
            sensor_data.left_frame.copy(), sensor_data.left_detections, sensor_data.left_tracking
        )
        sensor_data.right_frame_visualized = self.visualizer.draw_enriched_frame(
            sensor_data.right_frame.copy(), sensor_data.right_detections, sensor_data.right_tracking
        )
        return sensor_data
