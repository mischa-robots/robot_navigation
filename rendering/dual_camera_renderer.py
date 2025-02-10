import cv2
import numpy as np

class DualCameraRenderer:
    def __init__(self, window_name="Robot Navigation"):
        self.window_name = window_name

    def show(self, frames):
        """
        Combines the frames from multiple cameras and displays them.

        :param frames: Dictionary of frames, keyed by camera index.
        """
        processed_frames = []
        for i in sorted(frames.keys()):
            frame_copy = frames[i].copy()
            processed_frames.append(frame_copy)
        combined_frame = np.hstack(tuple(processed_frames))
        cv2.imshow(self.window_name, combined_frame)
