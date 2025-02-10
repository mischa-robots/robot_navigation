import threading
import time

class AutonomousNavigator:
    def __init__(self, capture, frame_processor, ws_client, strategy, decision_interval=0.2):
        """
        :param capture: Instance of DualCameraCapture (frames only).
        :param frame_processor: Instance of FrameProcessor (runs detection & tracking).
        :param ws_client: Instance of WebSocketClient.
        :param strategy: An instance of NavigationStrategy.
        :param decision_interval: Time (in seconds) between decision updates.
        """
        self.capture = capture
        self.frame_processor = frame_processor
        self.ws_client = ws_client
        self.strategy = strategy
        self.decision_interval = decision_interval
        self.running = True
        self.enabled = False  # Autonomous driving is off by default.
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self):
        while self.running:
            # Retrieve the latest frames from the capture module.
            left_frame = self.capture.frames.get("left")
            right_frame = self.capture.frames.get("right")
            
            # Skip if one of the frames is missing.
            if left_frame is None or right_frame is None:
                time.sleep(self.decision_interval)
                continue

            # Process the frames to get detections and tracking objects.
            sensor_data = self.frame_processor.process(left_frame, right_frame)

            # Get the navigation command.
            left_speed, right_speed = self.strategy.decide(sensor_data)
            if self.enabled:
                self.ws_client.send_command(left_speed, right_speed)
            time.sleep(self.decision_interval)

    def stop(self):
        self.running = False
        self.thread.join()
