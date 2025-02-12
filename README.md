# Robot Navigation

An autonomous robot navigation system powered by computer vision and AI, designed to enable robots to perceive their environment and navigate safely using dual camera streams.

![Robot](/assets/robots01.jpg)

## Overview

This project implements a sophisticated autonomous navigation system that combines real-time object detection, stereo vision, and intelligent path planning. The system processes dual RTSP camera streams using [YoloV11](https://docs.ultralytics.com/models/yolo11/) object detection to identify obstacles and guide robot movement through various navigation strategies.

The idea is that this project can run on a device that is connected to the robot via WiFi (ie. notebook with GPU) and also directly on the robot (ie. with a Jetson Nano).

## Key Features

- **Dual Camera Vision System**
  - Real-time processing of synchronized RTSP camera streams
  - Multi-threaded frame capture with automatic retry logic
  - Robust frame buffering and synchronization

- **Advanced Object Detection**
  - YOLO-based detection model for identifying robots and obstacles
  - Real-time distance estimation using detection metrics
  - Configurable object classification with support for walls and other robots

- **3D Object Tracking**
  - Kalman filter-based tracking system
  - Stereo triangulation for accurate position estimation
  - Predictive motion tracking capabilities

- **Flexible Navigation Strategies**
  - Modular architecture supporting multiple navigation approaches
  - Default reactive behavior strategy for obstacle avoidance
  - Extensible framework with support for:
    - Potential field navigation
    - Local mapping-based navigation
    - Reinforcement learning-based control

- **Robust Communication**
  - WebSocket-based robot control interface
  - Reliable command transmission with automatic reconnection
  - Clean shutdown handling

- **Real-time Visualization**
  - Configurable visualization modes
  - Detection and tracking visualization
  - Distance estimation display
  - Dual camera feed rendering

## Implemented navigation strategies:

- [x] ReactiveBehaviorStrategy
- [ ] PotentialFieldStrategy
- [ ] LocalMappingStrategy
- [ ] ReinforcementLearningStrategy
- [ ] DeepReinforcementLearningStrategy

## System Architecture

The project follows a modular architecture with clear separation of concerns:

```
robot_navigation/
├── camera/         # Camera stream handling
├── data/           # Configuration and metrics
├── detection/      # Object detection
├── navigation/     # Navigation strategies
├── network/        # Robot communication
├── processing/     # Frame processing pipeline
├── rendering/      # Visualization
├── tracking/       # 3D object tracking
└── visualizing/    # Frame annotation
```

The modules can be extended or simply exchanged through dependency injection.

## Requirements

- GPU (ie. notebook or PC NVidia RTX, installed cuda drivers, cudnn, pytorch etc)
- Python 3.12 with venv (or other environment as you like)
- OpenCV (compiled with cuda/pytorch support)
- YOLO (compatible with project's model format)
- WebSocket client support

## Getting Started

*WIP* : requirements.txt to install dependencies

1. Clone the repository
```bash
git clone https://github.com/mischa-robots/robot_navigation.git
cd robot_navigation
```

2. Configure your camera streams in `config.py`
3. Adjust detection metrics in `data/distances.json` if needed
4. Run the main application:
```bash
python main.py
```

## Contributing

Contributions are welcome! The modular architecture makes it easy to:
- Implement new navigation strategies
- Add support for different detection models
- Enhance visualization capabilities
- Improve tracking algorithms

To contribute, please fork this project, open a new branch, commit your changes into it and open a merge request :)

## License

    RobotNavigation - an implementation of different navigation strategies for autonomous robots.

    Copyright (C) 2025 Michael <Mischa> Schaefer

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
