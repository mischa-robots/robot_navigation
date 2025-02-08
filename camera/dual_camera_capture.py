import cv2
import numpy as np
import time
import threading
import os

class DualCameraCapture:
    def __init__(self, detector, robot_ip="192.168.129.84", stream_port=8554, num_cams=2):
        self.stream_urls = [f"rtsp://{robot_ip}:{stream_port}/cam{i}" for i in range(num_cams)]
        self.window_name = "Robot Cameras (Autonomous Mode)"
        self.frames = {i: None for i in range(num_cams)}
        self.detections = {i: None for i in range(num_cams)}
        self.running = True
        self.threads = []
        self.detector = detector

    def open_camera_stream(self, cam_index):
        attempts = 0
        cap = None
        while attempts < 3:
            cap = cv2.VideoCapture(self.stream_urls[cam_index], cv2.CAP_FFMPEG)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            if cap.isOpened():
                print(f"Camera {cam_index} stream opened successfully.")
                return cap
            else:
                attempts += 1
                print(f"Attempt {attempts} to open camera {cam_index} stream at {self.stream_urls[cam_index]} failed, retrying in 5 seconds...")
                time.sleep(5)
        return None

    def capture_frames(self, cam_index):
        cap = self.open_camera_stream(cam_index)
        if cap is None:
            print(f"Failed to open camera {cam_index} stream after 3 attempts. Shutting down.")
            os._exit(1)

        while self.running:
            ret, frame = cap.read()
            if ret:
                frame_height, frame_width = frame.shape[:2]

                # Run inference and extract detections without using the built-in drawing.
                detections = self.detector.detect(frame, frame_width, frame_height)

                # Use the raw frame (without YOLO's labels) so our boxes can be drawn
                self.frames[cam_index] = frame.copy()
                self.detections[cam_index] = detections
            else:
                print(f"Failed to grab frame from cam{cam_index}")
                time.sleep(0.1)
        cap.release()

    def start(self):
        for i in range(len(self.stream_urls)):
            thread = threading.Thread(target=self.capture_frames, args=(i,), daemon=True)
            thread.start()
            self.threads.append(thread)

    def stop(self):
        self.running = False
        for thread in self.threads:
            thread.join()

    def draw_enriched_frame(self, frame, detections):
        """
        Draw bounding boxes and labels with enriched distance information.
        """
        for det in detections:
            bbox = det["bbox"]
            label = det.get("label", "object")

            # Append the estimated distance to the label if available.
            if "distance" in det:
                display_text = f"{label} {det['confidence']:.2f}%: {det['distance']:.2f}m"
            else:
                display_text = f"{label} {det['confidence']:.2f}%: ??m"

            # Convert coordinates to integers.
            x1, y1, x2, y2 = map(int, bbox)
            # Draw rectangle around the object.

            if label == "robot":
                color = (255, 0, 0)
            else:
                color = (0, 255, 0)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, display_text, (x1, max(y1 - 10, 0)), cv2.FONT_HERSHEY_DUPLEX, 1, color, 1)
        return frame

    def show(self):
        if all(frame is not None for frame in self.frames.values()):
            processed_frames = []
            for i in sorted(self.frames.keys()):
                frame_copy = self.frames[i].copy()
                if self.detections[i]:
                    frame_copy = self.draw_enriched_frame(frame_copy, self.detections[i])
                processed_frames.append(frame_copy)
            combined_frame = np.hstack(tuple(processed_frames))
            cv2.imshow(self.window_name, combined_frame)


