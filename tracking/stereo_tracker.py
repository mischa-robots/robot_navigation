import cv2
import numpy as np
from filterpy.kalman import KalmanFilter

class Track:
    def __init__(self, initial_position, track_id):
        self.id = track_id
        self.kf = KalmanFilter(dim_x=6, dim_z=3)  # State: [x, y, z, vx, vy, vz]
        # Initialize state vector with the initial 3D position.
        self.kf.x[:3] = np.array(initial_position).reshape(3, 1)
        # Configure basic matrices (these should be tuned for your application).
        self.kf.F = np.eye(6)
        self.kf.H = np.hstack([np.eye(3), np.zeros((3, 3))])
        self.kf.P *= 1000.0
        self.kf.R = np.eye(3)
        self.kf.Q = np.eye(6)
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
        self.calibration_data = calibration_data  # Expected keys: 'P_left', 'P_right'
        self.tracks = []
        self.next_id = 0

    def triangulate(self, pt_left, pt_right, det_left=None):
        # Fallback: if calibration data is missing, use the left detection center and its distance.
        if not self.calibration_data or 'P_left' not in self.calibration_data or 'P_right' not in self.calibration_data:
            if det_left is not None and 'distance' in det_left:
                return [pt_left[0], pt_left[1], det_left['distance']]
            else:
                return [pt_left[0], pt_left[1], 1.0]
        else:
            P_left = self.calibration_data['P_left']
            P_right = self.calibration_data['P_right']
            point_left = np.array([[pt_left[0]], [pt_left[1]], [1]])
            point_right = np.array([[pt_right[0]], [pt_right[1]], [1]])
            point_4d = cv2.triangulatePoints(P_left, P_right, point_left, point_right)
            point_3d = (point_4d / point_4d[3])[:3].flatten()
            return point_3d

    def match_detections(self, detections_left, detections_right):
        # Assumes the detections are ordered similarly.
        return list(zip(detections_left, detections_right))

    def update(self, detections_left, detections_right):
        # Ensure each detection has a 'center' computed from its bbox.
        for det in detections_left:
            if 'center' not in det and 'bbox' in det:
                bbox = det['bbox']
                det['center'] = [ (bbox[0] + bbox[2]) / 2.0, (bbox[1] + bbox[3]) / 2.0 ]
        for det in detections_right:
            if 'center' not in det and 'bbox' in det:
                bbox = det['bbox']
                det['center'] = [ (bbox[0] + bbox[2]) / 2.0, (bbox[1] + bbox[3]) / 2.0 ]

        # Triangulate detections to obtain 3D points.
        matches = self.match_detections(detections_left, detections_right)
        detections_3d = []
        for det_left, det_right in matches:
            pt_left = det_left.get('center')
            pt_right = det_right.get('center')
            if pt_left is not None and pt_right is not None:
                pt_3d = self.triangulate(pt_left, pt_right, det_left)
                detections_3d.append(pt_3d)

        # Associate the 3D detections with existing tracks.
        for pt in detections_3d:
            matched = False
            for track in self.tracks:
                if np.linalg.norm(track.get_state() - pt) < 0.5:  # Distance threshold.
                    track.update(pt)
                    matched = True
                    break
            if not matched:
                new_track = Track(initial_position=pt, track_id=self.next_id)
                self.next_id += 1
                self.tracks.append(new_track)

        # Predict next state for all tracks.
        for track in self.tracks:
            track.predict()

        # Remove stale tracks.
        self.tracks = [track for track in self.tracks if track.age < 50]

        return self.tracks
