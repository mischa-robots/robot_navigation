import os
import sys
import cv2
import threading
import time

from robot_navigation.config import DISTANCES_PATH, MODEL_PATH, CROP_PATH
from robot_navigation.camera.dual_camera_capture import DualCameraCapture
from robot_navigation.camera.frame_cropper_pytorch import FrameCropper
from robot_navigation.data.metrics_loader import MetricsLoader
from robot_navigation.data.sensor_data_hub import SensorDataHub
from robot_navigation.detection.distance_estimator import DistanceEstimator
from robot_navigation.detection.yolo_detector import YoloDetector
from robot_navigation.visualizing.frame_visualizer import FrameVisualizer
from robot_navigation.processing.processing_pipeline_manager import ProcessingPipelineManager
from robot_navigation.processing.detection_processor import DetectionProcessor
from robot_navigation.processing.distance_estimation_processor import DistanceEstimationProcessor
from robot_navigation.processing.tracking_processor import TrackingProcessor
from robot_navigation.processing.visualizing_processor import VisualizingProcessor
from robot_navigation.network.websocket_client import WebSocketClient
from robot_navigation.navigation.autonomous_navigator import AutonomousNavigator
from robot_navigation.navigation.reactive_behavior_strategy import ReactiveBehaviorStrategy
from robot_navigation.rendering.dual_camera_renderer import DualCameraRenderer
from robot_navigation.rendering.sensor_data_renderer import SensorDataRenderer
from robot_navigation.tracking.deepsort_tracker import DeepSortTracker

def frame_processing_loop(capture, processing_pipeline_manager: ProcessingPipelineManager, frame_cropper, stop_event):
    """Continuously process frames and update the SensorDataHub."""
    while not stop_event.is_set():
        try:
            left_frame = capture.frames.get(0)
            right_frame = capture.frames.get(1)

            if left_frame is not None and right_frame is not None:
                left_frame, right_frame = frame_cropper.crop_frames(left_frame, right_frame)
                if left_frame is not None and right_frame is not None:
                    processing_pipeline_manager.process_and_update(left_frame, right_frame)
            else:
                time.sleep(0.01)
        
        except Exception as e:
            print(f"Error in processing loop: {e}")
            time.sleep(0.1)

def main():
    # Parse command-line arguments or set default values.
    robot_ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.129.84"
    stream_port = int(sys.argv[2]) if len(sys.argv) > 2 else 8554
    ws_port = int(sys.argv[3]) if len(sys.argv) > 3 else 8000

    stop_event = threading.Event()

    # Load distance metrics
    metrics_loader = MetricsLoader(DISTANCES_PATH)
    metrics = metrics_loader.load_metrics()

    # Initialize object detection model
    detector = YoloDetector(MODEL_PATH)
    distance_estimator = DistanceEstimator(metrics)

    # Initialize camera capture
    stream1_url = f"rtsp://{robot_ip}:{stream_port}/cam0"
    stream2_url = f"rtsp://{robot_ip}:{stream_port}/cam1"
    capture = DualCameraCapture(stream1_url, stream2_url)
    capture.start()

    # Initialize frame cropper
    cropper = FrameCropper(CROP_PATH)

    # Initialize tracker (can be None if disabled)
    tracker = DeepSortTracker()

    # Initialize frame visualizer
    visualizer = FrameVisualizer()

    # Create a shared sensor data hub
    sensor_data_hub = SensorDataHub()

    # Initialize Processing Pipeline Manager
    processing_pipeline_manager = ProcessingPipelineManager(sensor_data_hub)
    processing_pipeline_manager.register_module(DetectionProcessor(detector))
    processing_pipeline_manager.register_module(DistanceEstimationProcessor(distance_estimator))
    processing_pipeline_manager.register_module(TrackingProcessor(tracker))
    processing_pipeline_manager.register_module(VisualizingProcessor(visualizer))

    # Start frame processing in a separate thread
    processing_thread = threading.Thread(
        target=frame_processing_loop,
        args=(capture, processing_pipeline_manager, cropper, stop_event),
        daemon=True
    )
    processing_thread.start()

    # Initialize the renderer
    dual_camera_renderer = DualCameraRenderer(window_name="Robot Navigation")
    renderer = SensorDataRenderer(dual_camera_renderer)
    cv2.namedWindow("Robot Navigation", cv2.WINDOW_NORMAL)

    # Initialize WebSocket client
    ws_url = f"ws://{robot_ip}:{ws_port}/ws"
    ws_client = WebSocketClient(ws_url)

    # Instantiate navigation strategy
    strategy = ReactiveBehaviorStrategy()

    # Initialize Autonomous Navigator
    navigator = AutonomousNavigator(sensor_data_hub, ws_client, strategy, decision_interval=0.5)

    print("Press ESC to exit.")
    print("Press SPACE to toggle autonomous driving on/off.")
    print("Press R to toggle rendering enriched with object detection.")

    try:
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC key.
                break

            elif key == ord(' '):
                navigator.enabled = not navigator.enabled
                if not navigator.enabled:
                    ws_client.send_command(0, 0)
                print("Autonomous mode:", "ENABLED" if navigator.enabled else "DISABLED")

            elif key == ord('r'):
                renderer.render_enriched = not renderer.render_enriched
                print("Display mode:", "ENRICHED" if renderer.render_enriched else "RAW")

            sensor_data = sensor_data_hub.get_latest()
            if sensor_data is not None:
                #print("[DEBUG] rendering !")
                renderer.show(sensor_data)
            else:
                #print("[DEBUG] no sensor data available !")
                dual_camera_renderer.show(capture.frames)

    except KeyboardInterrupt:
        print("Keyboard interrupt received, shutting down.")
    finally:
        # Signal the processing thread to stop
        stop_event.set()
        # Wait for the processing thread to finish
        if processing_thread.is_alive():
            processing_thread.join(timeout=2.0)
        # Clean up GPU resources
        cropper.cleanup()

        ws_client.send_command(0, 0)
        # If the navigator was started, stop it.
        if 'navigator' in locals():
            navigator.stop()
        capture.stop()
        ws_client.close()
        cv2.destroyAllWindows()
        print("System closed.")

if __name__ == "__main__":
    main()
