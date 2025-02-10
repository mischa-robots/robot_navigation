# robot_navigation

The goal of the project is to develop an autonomously driving robot that uses cameras to see the environment and avoid obstacles.

## project description

This project implements an AI-based robot navigation system that uses a YOLO object detector to process dual RTSP camera streams.
It estimates distances using detection metrics (loaded from a JSON file) and selects driving commands via a navigation strategy (default: reactive behavior).
Commands are sent to the robot over a WebSocket connection to drive the robot.

## github link

https://github.com/mischa-robots/robot_navigation

## project structure

```
robot_navigation/
    ├── config.py
    ├── distances.json
    ├── main.py
    ├── object_metrics.py
    ├── camera/
    │   ├── __init__.py
    │   └── dual_camera_capture.py
    ├── model/
    │   ├── __init__.py
    │   └── yolov11.py
    ├── navigation/
    │   ├── __init__.py
    │   ├── local_mapping_strategy.py <== local mapping navigation strategy; not implemented yet
    │   ├── navigation_strategy.py  <== abstract class / strategy design pattern
    │   ├── navigator.py
    │   ├── potential_field_strategy.py <== potential field navigation strategy; not implemented yet
    │   ├── reactive_behavior_strategy.py <== reactive behavior navigation strategy; Work In Progress
    │   └── reinforcement_learning_strategy.py <== reinforcement learning navigation strategy; not implemented yet
    └── network/
        ├── __init__.py
        └── websocket_client.py
```

## file contents

```
================================================
File: config.py
================================================
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'yolo11m_robot_detect_v2.engine')
DISTANCES_PATH = os.path.join(BASE_DIR, 'distances.json')

# Mapping from trained YoloV11 model class id to label.
CLASS_MAPPING = {
    0: 'robot',
    1: 'wall_bottom',
    2: 'wall_corner',
    3: 'wall_left',
    4: 'wall_right',
    5: 'wall_top'
}


================================================
File: distances.json
================================================
{
  "wall_corner": {
    "min_height_ratio": 0.06,
    "max_height_ratio": 1.0,
    "min_width_ratio": 0.03,
    "max_width_ratio": 0.6,
    "min_aspect_ratio": 0.2,
    "max_aspect_ratio": 1.0,
    "estimated_min_distance": 0.1,
    "estimated_max_distance": 2.2
  },
  "wall_top": { # same structure as wall_corner
  },
  "wall_right": { # same structure as wall_corner
  },
  "wall_bottom": { # same structure as wall_corner
  },
  "wall_left": { # same structure as wall_corner
  },
  "robot": { # same structure as wall_corner
  }
}

================================================
File: object_metrics.py
================================================
from dataclasses import dataclass

### this dataclass structure coresponds to the values in 'distances.json'

@dataclass
class ObjectMetrics:
    class_name: str
    min_height_ratio: float
    max_height_ratio: float
    min_width_ratio: float
    max_width_ratio: float
    min_aspect_ratio: float
    max_aspect_ratio: float
    estimated_min_distance: float
    estimated_max_distance: float

================================================
File: main.py
================================================
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
    ### Reads JSON from json_path, iterates over each label and its metrics,
    ### instantiates an ObjectMetrics object with parameters such as min/max height/width ratios,
    ### and returns a dictionary mapping each label to its corresponding ObjectMetrics.
    return metrics_dict

def main():
    ### Parses command line arguments for robot IP, stream port, and WebSocket port;
    ### loads distance estimation metrics from a JSON file;
    ### initializes the YOLO object detection model, dual camera capture, and WebSocket client;
    ### sets up a ReactiveBehaviorStrategy and an AutonomousNavigator to process detections and send drive commands;
    ### creates an OpenCV window to display camera frames and toggles autonomous mode based on key events;
    ### gracefully shuts down all components upon exit.
    
if __name__ == "__main__":
    main()


================================================
File: camera/dual_camera_capture.py
================================================
import cv2
import numpy as np
import time
import threading
import os

class DualCameraCapture:
    def __init__(self, detector, robot_ip="192.168.129.84", stream_port=8554, num_cams=2):
        ### Initializes DualCameraCapture by constructing stream URLs for each camera using the robot_ip and stream_port,
        ### and sets up data structures to hold frames and detection results, along with the provided object detector.
        
    def open_camera_stream(self, cam_index):
        ### Attempts to open the camera stream for the given cam_index using cv2.VideoCapture with up to 3 retries;
        ### returns the VideoCapture object if successful, or None if all attempts fail.
        return cap

    def capture_frames(self, cam_index):
        ### Opens the camera stream for cam_index (exiting the program if it fails after 3 attempts);
        ### continuously reads frames while running is True, processes each frame with the detector to obtain detections,
        ### and updates the frames and detections dictionaries; releases the camera resource when stopping.
        
    def start(self):
        ### Starts the capture process by spawning a separate daemon thread for each camera stream that runs capture_frames.
        
    def stop(self):
        ### Stops the frame capturing by setting the running flag to False and joining all the spawned threads.
        
    def draw_enriched_frame(self, frame, detections):
        ### Iterates over the list of detections to draw bounding boxes and labels (including confidence and estimated distance)
        ### on the provided frame; returns the annotated frame.
        return frame

    def show(self):
        ### If frames from all cameras are available, processes each frame by drawing detections,
        ### horizontally stacks them into a single combined frame, and displays it in an OpenCV window.
        


================================================
File: model/yolov11.py
================================================
from ultralytics import YOLO
from robot_navigation.config import MODEL_PATH, CLASS_MAPPING

class YOLOv11Detector:
    def __init__(self, metrics, model_path):
        ### Initializes YOLOv11Detector with provided object metrics and loads the YOLO model from model_path.
        
    def predict(self, frame):
        ### Runs inference on the given frame using the YOLO model and returns the raw predictions.
        return self.model.predict(frame, stream=False, device='cuda', verbose=False)

    def extract_detections(self, predictions, frame_width, frame_height):
        ### Iterates over the prediction boxes to extract detection details:
        ### - Converts box coordinates to pixel values,
        ### - Retrieves confidence scores and class labels,
        ### - Calculates the observed height ratio and estimates the object distance via linear interpolation based on metrics,
        ### - Constructs and returns a list of detection dictionaries containing label, bbox, confidence, camera dimensions, and estimated distance.
        return detections

    def detect(self, frame, frame_width, frame_height):
        ### Performs detection on the frame by running inference and extracting detection details using frame dimensions and object metrics.
        return detections


================================================
File: navigation/__init__.py
================================================
from .navigation_strategy import NavigationStrategy
from .reactive_behavior_strategy import ReactiveBehaviorStrategy
from .potential_field_strategy import PotentialFieldStrategy
from .local_mapping_strategy import LocalMappingStrategy
from .reinforcement_learning_strategy import ReinforcementLearningStrategy

__all__ = [
    "NavigationStrategy",
    "ReactiveBehaviorStrategy",
    "PotentialFieldStrategy",
    "LocalMappingStrategy",
    "ReinforcementLearningStrategy",
]


================================================
File: navigation/local_mapping_strategy.py
================================================
from robot_navigation.navigation.navigation_strategy import NavigationStrategy

class LocalMappingStrategy(NavigationStrategy):
    def decide(self, detections: list) -> tuple[float, float]:
        ### Placeholder for local mapping and lightweight planning:
        ### Intended to analyze detections and compute appropriate wheel speeds;
        ### Currently returns a default command (1.0, 1.0).
        return 1.0, 1.0


================================================
File: navigation/navigation_strategy.py
================================================
from abc import ABC, abstractmethod

class NavigationStrategy(ABC):
    @abstractmethod
    def decide(self, detections: list) -> tuple[float, float]:
        """
        Given a list of detection dicts, return (left_speed, right_speed).
        Speeds are values in [-1.0, 1.0].
        """
        pass


================================================
File: navigation/navigator.py
================================================
import threading
import time

class AutonomousNavigator:
    def __init__(self, capture, ws_client, strategy, decision_interval=0.2):
        ### Initializes AutonomousNavigator with the provided capture, WebSocket client, and navigation strategy;
        ### sets the decision interval and starts a background daemon thread to continuously process detections and send drive commands.
        
    def run(self):
        ### Continuously aggregates detections from all camera streams,
        ### computes left and right wheel speeds using the navigation strategy,
        ### sends commands via the WebSocket client if autonomous mode is enabled,
        ### and pauses for decision_interval seconds between iterations.
        
    def stop(self):
        ### Stops the autonomous navigation loop by setting the running flag to False and joining the background thread.
        


================================================
File: navigation/potential_field_strategy.py
================================================
from robot_navigation.navigation.navigation_strategy import NavigationStrategy

class PotentialFieldStrategy(NavigationStrategy):
    def decide(self, detections: list) -> tuple[float, float]:
        ### Placeholder for potential field-based navigation:
        ### Intended to compute wheel speeds based on repulsive/attractive forces from obstacles;
        ### Currently returns a default command (1.0, 1.0).
        return 1.0, 1.0


================================================
File: navigation/reactive_behavior_strategy.py
================================================
from robot_navigation.navigation.navigation_strategy import NavigationStrategy

# Define critical thresholds.
SAFE_DISTANCE = 0.15  # Base safe distance (meters)
MARGIN = 0.05         # Additional margin (meters)

class ReactiveBehaviorStrategy(NavigationStrategy):

    def decide(self, detections: list) -> tuple[float, float]:
        # Default: stop the robot when no detections available or no decision can be made:
        left_cmd = 0.0
        right_cmd = 0.0

        ### TODO
        ### Analyze the list of detections to determine navigation commands

        return left_cmd, right_cmd


================================================
File: navigation/reinforcement_learning_strategy.py
================================================
from robot_navigation.navigation.navigation_strategy import NavigationStrategy

class ReinforcementLearningStrategy(NavigationStrategy):
    def decide(self, detections: list) -> tuple[float, float]:
        ### Placeholder for reinforcement learning-based navigation:
        ### Intended to use a trained RL model to determine wheel speeds based on detections;
        ### Currently returns a default command (1.0, 1.0).
        return 1.0, 1.0


================================================
File: network/websocket_client.py
================================================
import asyncio
import websockets
import json
import threading

class WebSocketClient:
    def __init__(self, ws_url):
        ### Initializes WebSocketClient with the provided ws_url;
        ### sets up an asyncio event loop and a background thread to run it,
        ### and initiates an asynchronous connection to the WebSocket server.
        
    def run_loop(self):
        ### Configures the asyncio event loop and runs it indefinitely.
        
    async def connect(self):
        ### Asynchronously attempts to connect to the WebSocket server at ws_url with disabled automatic pings;
        ### on success, stores the WebSocket connection; on failure, logs the error and sets ws to None.
        
    def send_command(self, left, right):
        ### Sends a command containing left and right wheel speeds via the WebSocket connection if available;
        ### if not connected, logs an error message.
        
    async def _send_command(self, left, right):
        ### Asynchronously sends a JSON-formatted command with left and right speeds over the WebSocket;
        ### if an error occurs during sending, logs the error and attempts to reconnect.
        
    def close(self):
        ### Closes the active WebSocket connection (if any) and stops the asyncio event loop.
```