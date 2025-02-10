from ultralytics import YOLO
from robot_navigation.config import CLASS_MAPPING

class YoloDetector:
    def __init__(self, metrics, model_path):
        """
        :param metrics: A dict mapping object labels to an ObjectMetrics instance.
        """
        self.metrics = metrics
        self.model = YOLO(model_path, task='detect')

    def predict(self, frame):
        """Run inference on a frame."""
        return self.model.predict(frame, stream=False, device='cuda', verbose=False)

    def extract_detections(self, frame, predictions):
        """
        Given a YOLO result as predictions, extract a list of dictionaries for each detection.
        Each dictionary contains:
        - label: the detected class label
        - bbox: [x1, y1, x2, y2] (in pixels)
        - confidence: confidence score (float)
        - camera_width, camera_height: for computing relative area
        - distance: estimated distance based on metrics
        """
        detections = []
        if not hasattr(predictions, 'boxes') or predictions.boxes is None:
            return detections

        frame_width = frame.shape[1]
        frame_height = frame.shape[0]

        for box in predictions.boxes:
            xyxy = box.xyxy[0].cpu().numpy().tolist()  # [x1, y1, x2, y2]
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            label = CLASS_MAPPING.get(cls_id, str(cls_id))

            detection_height = xyxy[3] - xyxy[1]
            observed_height_ratio = detection_height / frame_height
            metrics = self.metrics[label]

            # Simple stupid distance estimation using linear interpolation between min and max metrics.
            if observed_height_ratio <= metrics.min_height_ratio:
                estimated_distance = metrics.estimated_max_distance
            elif observed_height_ratio >= metrics.max_height_ratio:
                estimated_distance = metrics.estimated_min_distance
            else:
                estimated_distance = metrics.estimated_min_distance + (metrics.estimated_max_distance - metrics.estimated_min_distance) * (1 / observed_height_ratio - 1 / metrics.max_height_ratio) / (1 / metrics.min_height_ratio - 1 / metrics.max_height_ratio)

            detections.append({
                "label": label,
                "bbox": xyxy,
                "confidence": conf,
                "camera_width": frame_width,
                "camera_height": frame_height,
                "distance": estimated_distance
            })
        return detections
    
    def detect(self, frame):
        predictions = self.predict(frame)
        detections = self.extract_detections(frame, predictions[0])
        return detections
