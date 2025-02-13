import sys
import cv2
import threading
import time

from robot_navigation.config import DISTANCES_PATH, MODEL_PATH, CROP_PATH
from robot_navigation.camera.dual_camera_capture import DualCameraCapture
from robot_navigation.camera.frame_cropper_pytorch import FrameCropper
from robot_navigation.data.metrics_loader import MetricsLoader
from robot_navigation.data.sensor_data_hub import SensorDataHub
from robot_navigation.detection.yolo_detector import YoloDetector
from robot_navigation.tracking.stereo_tracker import StereoTracker
from robot_navigation.visualizing.frame_visualizer import FrameVisualizer
from robot_navigation.processing.frame_processor import FrameProcessor
from robot_navigation.network.websocket_client import WebSocketClient
from robot_navigation.navigation.autonomous_navigator import AutonomousNavigator
from robot_navigation.navigation.reactive_behavior_strategy import ReactiveBehaviorStrategy
from robot_navigation.rendering.dual_camera_renderer import DualCameraRenderer
from robot_navigation.rendering.sensor_data_renderer import SensorDataRenderer

def frame_processing_loop(capture, frame_processor, frame_cropper, stop_event):
    """Continuously process frames and update the SensorDataHub."""
    while not stop_event.is_set():
        try:
            left_frame = capture.frames.get(0)
            right_frame = capture.frames.get(1)

            if left_frame is not None and right_frame is not None:
                # Process frames in chunks
                left_frame, right_frame = frame_cropper.crop_frames(left_frame, right_frame)
                if left_frame is not None and right_frame is not None:
                    frame_processor.process_and_update(left_frame, right_frame)
            else:
                time.sleep(0.01)
                
        except Exception as e:
            print(f"Error in processing loop: {e}")
            time.sleep(0.1)

def main():
    # Parse command-line arguments.
    robot_ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.129.84"
    stream_port = int(sys.argv[2]) if len(sys.argv) > 2 else 8554
    ws_port = int(sys.argv[3]) if len(sys.argv) > 3 else 8000

    stop_event = threading.Event()

    # Load distance metrics.
    metrics_loader = MetricsLoader(DISTANCES_PATH)
    metrics = metrics_loader.load_metrics()

    # Initialize object detection model.
    detector = YoloDetector(metrics, MODEL_PATH)

    # Initialize frame cropper for horizontal frames adjustment
    cropper = FrameCropper(CROP_PATH)

    # Initialize a camera capture module
    stream1_url = f"rtsp://{robot_ip}:{stream_port}/cam0"
    stream2_url = f"rtsp://{robot_ip}:{stream_port}/cam1"
    capture = DualCameraCapture(stream1_url, stream2_url)
    capture.start()

    # Initialize the stereo tracker.
    calibration_data = {}  # Replace with actual calibration data if available.
    tracker = StereoTracker(calibration_data)

    # Initialize the frame visualizer.
    visualizer = FrameVisualizer()

    # Create a shared sensor data hub.
    sensor_data_hub = SensorDataHub()

    # Create the FrameProcessor with the sensor data hub.
    frame_processor = FrameProcessor(sensor_data_hub, detector, tracker, visualizer)

    # Start a thread for frame processing.
    processing_thread = threading.Thread(target=frame_processing_loop, args=(capture, frame_processor, cropper, stop_event), daemon=True)
    processing_thread.start()

    # Initialize the DualCameraRenderer for displaying frames.
    dual_camera_renderer = DualCameraRenderer(window_name="Robot Navigation")
    renderer = SensorDataRenderer(dual_camera_renderer)

    # Create a named window.
    cv2.namedWindow("Robot Navigation", cv2.WINDOW_NORMAL)

    # Initialize the WebSocket client.
    ws_url = f"ws://{robot_ip}:{ws_port}/ws"
    ws_client = WebSocketClient(ws_url)

    # Instantiate a navigation strategy.
    strategy = ReactiveBehaviorStrategy()

    # Optionally, instantiate the AutonomousNavigator.
    # (If you remove or comment out the following line, the rest of the system will still run.)
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
                #time.sleep(0.1)

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
