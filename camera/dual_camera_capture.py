import cv2
import time
import threading
import os

class DualCameraCapture:
    def __init__(self, stream1_url, stream2_url):
        self.stream_urls = [stream1_url, stream2_url]
        self.frames = {i: None for i in range(2)}
        self.running = True
        self.threads = []

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
                # Save a copy of the raw frame
                self.frames[cam_index] = frame.copy()
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
