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
Project Directory structure:
└── robot_navigation/
    ├── __init__.py
    ├── config.py
    ├── main.py
    ├── assets/
    ├── camera/
    │   ├── __init__.py
    │   ├── dual_camera_capture.py
    │   ├── frame_cropper.py
    │   ├── frame_cropper_cuda.py
    │   └── frame_cropper_pytorch.py
    ├── data/
    │   ├── __init__.py
    │   ├── crop_calibration.json
    │   ├── distances.json
    │   ├── metrics_loader.py
    │   ├── object_metrics.py
    │   ├── sensor_data.py
    │   └── sensor_data_hub.py
    ├── detection/
    │   ├── __init__.py
    │   └── yolo_detector.py
    ├── navigation/
    │   ├── __init__.py
    │   ├── autonomous_navigator.py
    │   ├── local_mapping_strategy.py
    │   ├── navigation_strategy.py
    │   ├── potential_field_strategy.py
    │   ├── reactive_behavior_strategy.py
    │   └── reinforcement_learning_strategy.py
    ├── network/
    │   ├── __init__.py
    │   └── websocket_client.py
    ├── processing/
    │   ├── __init__.py
    │   ├── depth_estimation_processor.py
    │   ├── detection_processor.py
    │   ├── processing_module.py
    │   ├── processing_pipeline_manager.py
    │   ├── tracking_processor.py
    │   └── visualizing_processor.py
    ├── rendering/
    │   ├── __init__.py
    │   ├── dual_camera_renderer.py
    │   └── sensor_data_renderer.py
    ├── tracking/
    │   ├── __init__.py
    │   └── empty_tracker.py
    └── visualizing/
        ├── __init__.py
        └── frame_visualizer.py
```

## file contents description

```
================================================
File: config.py
================================================
Contains configuration constants including paths and class mappings for a robot detection model. Defines BASE_DIR, MODEL_PATH, and CLASS_MAPPING for robot and wall detection classes.

================================================
File: main.py
================================================
Main entry point that initializes and orchestrates the robot navigation system. Sets up camera captures, object detection, tracking, visualization, and autonomous navigation components. Implements a main loop that processes frames and handles user input for toggling autonomous mode and visualization options.

Key components initialized:
- Dual camera capture with optional cropping for camera adjustment (config based)
- YOLO object detector
- Stereo tracker
- Frame visualizer
- WebSocket client for robot control
- Autonomous navigator with reactive behavior strategy

================================================
File: camera/dual_camera_capture.py
================================================
Handles dual camera stream capture using OpenCV. Uses threading to continuously capture frames from two RTSP streams. Main features:
- Stream connection management with retry logic
- Multi-threaded frame capture
- Frame buffering
- Graceful shutdown handling

================================================
File: frame_cropper.py
================================================
CPU-based implementation of frame cropping for stereo camera feeds.
Uses NumPy optimizations for efficient frame cropping operations.

================================================
File: frame_cropper_cuda.py
================================================
CUDA-accelerated implementation using OpenCV's GPU module for high-performance frame cropping.
Leverages direct GPU memory operations for stereo camera feeds. Main features:
- GPU memory pre-allocation and CUDA stream management for asynchronous operations

================================================
File: frame_cropper_pytorch.py
================================================
PyTorch-based GPU implementation for frame cropping using tensor operations.
Provides flexible GPU acceleration with PyTorch's CUDA support. Main features:
- Automatic GPU/CPU device selection and PyTorch tensor-based operations

================================================
File: data/distances.json
================================================
Configuration file containing object detection metrics including:
- Height/width ratio constraints
- Aspect ratio limits
- Estimated distance ranges
For different object types: wall corners, walls (top/right/bottom/left), and robots

================================================
File: data/metrics_loader.py
================================================
Loads and parses object detection metrics from distances.json into ObjectMetrics instances.

================================================
File: data/object_metrics.py
================================================
Defines ObjectMetrics dataclass for storing detection parameters including ratio constraints and distance estimates.

================================================
File: data/sensor_data.py
================================================
Defines SensorData dataclass for storing:
- Raw frames from both cameras
- Visualized frames
- Detection results
- Tracking data

================================================
File: data/sensor_data_hub.py
================================================
Thread-safe container for sharing the latest sensor data between components using mutex locks.

================================================
File: detection/yolo_detector.py
================================================
YOLO-based object detector implementation. Features:
- Loads pretrained model for robot/wall detection
- Performs inference on camera frames
- Extracts and formats detections with distance estimation
- Maps class IDs to labels

================================================
File: navigation/autonomous_navigator.py
================================================
Implements autonomous navigation control loop:
- Runs in separate thread
- Retrieves latest sensor data
- Uses strategy to compute motor commands
- Sends commands via WebSocket

================================================
File: navigation/*_strategy.py
================================================
Multiple navigation strategy implementations:
- NavigationStrategy: Abstract base class
- ReactiveBehaviorStrategy: Simple reactive control
- PotentialFieldStrategy: Stub for potential field method
- LocalMappingStrategy: Stub for mapping-based navigation
- ReinforcementLearningStrategy: Stub for RL-based control

================================================
File: network/websocket_client.py
================================================
Handles WebSocket communication with robot:
- Async connection management
- Command serialization and transmission
- Automatic reconnection
- Clean shutdown

================================================
File: processing/depth_estimation_processor.py
================================================
Implements a processing module for depth estimation.

================================================
File: processing/detection_processor.py
================================================
Handles object detection processing for both camera frames. Main features:
- Stores detection results in the SensorData object

================================================
File: processing/processing_module.py
================================================
Defines abstract base class (ABC) for all processing modules in the pipeline:
- Establishes common interface for processing components with the process function
- Enforces sensor data input/output contract

================================================
File: processing/processing_pipeline_manager.py
================================================
Orchestrates the modular processing pipeline. Main features:
- Manages sequence of processing modules
- Allows dynamic registration of modules
- Creates and initializes SensorData object
- Updates central SensorDataHub with processed results
- Processes frames through the complete pipeline

================================================
File: processing/tracking_processor.py
================================================
Implements tracking module for object persistence.

================================================
File: processing/visualizing_processor.py
================================================
Handles visualization processing of detected and tracked objects.

================================================
File: rendering/dual_camera_renderer.py
================================================
Handles display of dual camera feeds:
- Combines frames side by side
- Maintains display window
- Handles frame synchronization

================================================
File: rendering/sensor_data_renderer.py
================================================
Manages visualization modes:
- Raw camera feeds
- Enhanced visualization with detections
- Handles missing/incomplete data

================================================
File: tracking/empty_tracker.py
================================================
Implements object tracking: empty file as placeholder for future implementation

================================================
File: visualizing/frame_visualizer.py
================================================
Handles detection visualization:
- Draws bounding boxes
- Adds labels and confidence scores
- Shows distance estimates
- Color codes different object types
```
