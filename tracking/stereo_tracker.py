import cv2
import numpy as np
from filterpy.kalman import KalmanFilter

class Track:
    def __init__(self, initial_position, track_id):
        self.id = track_id
        self.kf = KalmanFilter(dim_x=6, dim_z=3)  # State: [x, y, z, vx, vy, vz]
        # Initialize state vector with the initial 3D position:
        self.kf.x[:3] = np.array(initial_position).reshape(3, 1)
        # Configure the rest of the Kalman filter (F, H, P, Q, R) as needed...
        self.age = 0
        self.hits = 1

    def predict(self):
        self.kf.predict()
        self.age += 1

    def update(self, measurement):
        self.kf.update(np.array(measurement).reshape(3, 1))
        self.hits += 1

    def get_state(self):
        return self.kf.x[:3].flatten()

class StereoTracker:
    def __init__(self, calibration_data):
        self.calibration_data = calibration_data  # Contains stereo camera calibration (P_left, P_right, etc.)
        self.tracks = []
        self.next_id = 0

    def triangulate(self, pt_left, pt_right):
        """
        Given corresponding points in the left and right frames,
        use the calibration data to triangulate a 3D point.
        """
        P_left = self.calibration_data['P_left']
        P_right = self.calibration_data['P_right']
        point_left = np.array([[pt_left[0]], [pt_left[1]], [1]])
        point_right = np.array([[pt_right[0]], [pt_right[1]], [1]])
        point_4d = cv2.triangulatePoints(P_left, P_right, point_left, point_right)
        point_3d = (point_4d / point_4d[3])[:3].flatten()
        return point_3d

    def match_detections(self, detections_left, detections_right):
        """
        This function matches detections from the left and right cameras.
        In a real implementation, you might use epipolar constraints and/or object appearance.
        Here we assume that the detections are ordered similarly.
        """
        return list(zip(detections_left, detections_right))

    def update(self, detections_left, detections_right):
        # Step 1: Triangulate detections to 3D positions
        matches = self.match_detections(detections_left, detections_right)
        detections_3d = []
        for det_left, det_right in matches:
            # For example, assume each detection dict has a 'center' key with (x, y)
            pt_left = det_left.get('center')
            pt_right = det_right.get('center')
            if pt_left is not None and pt_right is not None:
                pt_3d = self.triangulate(pt_left, pt_right)
                detections_3d.append(pt_3d)

        # Step 2: Associate 3D detections with existing tracks using a simple distance threshold.
        for pt in detections_3d:
            matched = False
            for track in self.tracks:
                if np.linalg.norm(track.get_state() - pt) < 0.5:  # Threshold can be tuned.
                    track.update(pt)
                    matched = True
                    break
            if not matched:
                # Create a new track for this detection
                new_track = Track(initial_position=pt, track_id=self.next_id)
                self.next_id += 1
                self.tracks.append(new_track)

        # Step 3: Predict next state for all tracks
        for track in self.tracks:
            track.predict()

        # Optionally, remove stale tracks (e.g., based on age or missed updates)
        self.tracks = [track for track in self.tracks if track.age < 50]

        return self.tracks
