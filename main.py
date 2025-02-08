import json
import sys
from robot_navigation.camera.dual_camera_capture import DualCameraCapture
from robot_navigation.config import DISTANCES_PATH
from robot_navigation.network.websocket_client import WebSocketClient
from robot_navigation.navigation.navigator import AutonomousNavigator
from robot_navigation.navigation.reactive_behavior_strategy import ReactiveBehaviorStrategy
from robot_navigation.object_metrics import ObjectMetrics
from robot_navigation.model.yolov11 import YOLOv11Detector
from robot_navigation.config import MODEL_PATH, CLASS_MAPPING

def load_metrics(json_path: str) -> dict:
    with open(json_path, "r") as f:
        metrics_data = json.load(f)
    metrics_dict = {}
    for label, data in metrics_data.items():
        metrics_dict[label] = ObjectMetrics(
            class_name=label,
            min_height_ratio=data["min_height_ratio"],
            max_height_ratio=data["max_height_ratio"],
            min_width_ratio=data["min_width_ratio"],
            max_width_ratio=data["max_width_ratio"],
            min_aspect_ratio=data["min_aspect_ratio"],
            max_aspect_ratio=data["max_aspect_ratio"],
            estimated_min_distance=data["estimated_min_distance"],
            estimated_max_distance=data["estimated_max_distance"]
        )
    return metrics_dict

def main():
    robot_ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.129.84"
    stream_port = int(sys.argv[2]) if len(sys.argv) > 2 else 8554
    ws_port = int(sys.argv[3]) if len(sys.argv) > 3 else 8000

    # Load the distance estimation metrics from the JSON file.
    metrics = load_metrics(DISTANCES_PATH)

    # load object detection model
    yoloDetector = YOLOv11Detector(metrics, MODEL_PATH)

    # Initialize camera capture
    capture = DualCameraCapture(yoloDetector, robot_ip=robot_ip, stream_port=stream_port)
    capture.start()

    # Initialize WebSocket communication.
    ws_url = f"ws://{robot_ip}:{ws_port}/ws"
    ws_client = WebSocketClient(ws_url)

    # Pass the metrics to the ReactiveBehaviorStrategy.
    strategy = ReactiveBehaviorStrategy()
    navigator = AutonomousNavigator(capture, ws_client, strategy, decision_interval=0.5)

    import cv2
    cv2.namedWindow(capture.window_name, cv2.WINDOW_NORMAL)
    print("Press SPACE to toggle autonomous driving on/off. (Default is OFF)")
    try:
        while True:
            capture.show()
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
