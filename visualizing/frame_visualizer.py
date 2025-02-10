import cv2

class FrameVisualizer:
    def __init__(self):
        # You can initialize default fonts, colors, or any parameters here.
        self.font = cv2.FONT_HERSHEY_DUPLEX
        self.robot_color = (255, 0, 0)
        self.wall_color = (0, 255, 0)
        self.corner_color = (0, 0, 255)

    def draw_enriched_frame(self, frame, detections):
        """
        Draw bounding boxes, labels, and distance info on the frame.
        
        :param frame: The image frame as a NumPy array.
        :param detections: List of detection dictionaries, where each dictionary should
                           have at least the keys "bbox", "label", "confidence", and optionally "distance".
        :return: The annotated frame.
        """
        for det in detections:
            bbox = det.get("bbox")
            label = det.get("label", "object")
            confidence = det.get("confidence", 0)
            distance = det.get("distance", None)
            
            if distance is not None:
                display_text = f"{label} {confidence:.2f}%: {distance:.2f}m"
            else:
                display_text = f"{label} {confidence:.2f}%: ??m"
            
            # Convert coordinates to integers.
            x1, y1, x2, y2 = map(int, bbox)
            # Choose a color based on label.
            if label == "robot":
                color = self.robot_color
            elif label == "wall_corner":
                color = self.corner_color
            else:
                color = self.wall_color
            
            # Draw the bounding box and label.
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, display_text, (x1, max(y1 - 10, 0)), self.font, 1, color, 1)
        return frame
