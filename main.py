import sys
import cv2
from robot_navigation.camera.dual_camera_capture import DualCameraCapture
from robot_navigation.config import DISTANCES_PATH, MODEL_PATH
from robot_navigation.data.metrics_loader import MetricsLoader
from robot_navigation.network.websocket_client import WebSocketClient
from robot_navigation.navigation.autonomous_navigator import AutonomousNavigator
from robot_navigation.navigation.reactive_behavior_strategy import ReactiveBehaviorStrategy
from robot_navigation.data.object_metrics import ObjectMetrics
from robot_navigation.detection.yolo_detector import YoloDetector
from robot_navigation.tracking.stereo_tracker import StereoTracker
from robot_navigation.processing.frame_processor import FrameProcessor
from robot_navigation.visualizing.frame_visualizer import FrameVisualizer
from robot_navigation.rendering.dual_camera_renderer import DualCameraRenderer

def main():
    robot_ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.129.84"
    stream_port = int(sys.argv[2]) if len(sys.argv) > 2 else 8554
    ws_port = int(sys.argv[3]) if len(sys.argv) > 3 else 8000

    # load distance metrics
    metrics_loader = MetricsLoader(DISTANCES_PATH)
    metrics = metrics_loader.load_metrics()

    # load object detection model
    object_detector = YoloDetector(metrics, MODEL_PATH)

    # Initialize a camera capture module
    stream1_url = f"rtsp://{robot_ip}:{stream_port}/cam0"
    stream2_url = f"rtsp://{robot_ip}:{stream_port}/cam1"
    capture = DualCameraCapture(stream1_url, stream2_url)
    capture.start()

    # Initialize the stereo tracker with your calibration data (assumed to be loaded inside the tracker).
    # For instance, you might load calibration data from a file.
    calibration_data = {}  # Replace with actual calibration loading.
    object_tracker = StereoTracker(calibration_data)

    frame_visualizer = FrameVisualizer()
    frame_processor = FrameProcessor(object_detector, object_tracker, frame_visualizer)

    renderer = DualCameraRenderer()

    # Initialize the WebSocket client.
    ws_url = f"ws://{robot_ip}:{ws_port}/ws"
    ws_client = WebSocketClient(ws_url)

    # Instantiate a navigation strategy.
    strategy = ReactiveBehaviorStrategy()

    # Create the navigator, injecting the capture, frame processor, WebSocket client, and strategy.
    navigator = AutonomousNavigator(capture, frame_processor, ws_client, strategy, decision_interval=0.5)

    cv2.namedWindow(capture.window_name, cv2.WINDOW_NORMAL)
    print("Press SPACE to toggle autonomous driving on/off. (Default is OFF)")
    try:
        while True:
            capture.show()  # This shows the latest captured frames.
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC key to exit.
                break
            elif key == ord(' '):
                navigator.enabled = not navigator.enabled
                if not navigator.enabled:
                    ws_client.send_command(0, 0)
                print("Autonomous mode:", "ENABLED" if navigator.enabled else "DISABLED")
    except KeyboardInterrupt:
        print("Keyboard interrupt received, shutting down.")
    finally:
        print("Shutting down...")
        ws_client.send_command(0, 0)
        navigator.stop()
        capture.stop()
        ws_client.close()
        cv2.destroyAllWindows()
        print("System closed.")

if __name__ == "__main__":
    main()
