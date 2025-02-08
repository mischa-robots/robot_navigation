import threading
import time

class AutonomousNavigator:
    def __init__(self, capture, ws_client, strategy, decision_interval=0.2):
        """
        :param capture: Instance of DualCameraCapture.
        :param ws_client: Instance of WebSocketClient.
        :param strategy: An instance of NavigationStrategy.
        :param decision_interval: Time (in seconds) between decision updates.
        """
        self.capture = capture
        self.ws_client = ws_client
        self.strategy = strategy
        self.decision_interval = decision_interval
        self.running = True
        self.enabled = False  # Autonomous driving is off by default.
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self):
        while self.running:
            all_detections = []
            for det_list in self.capture.detections.values():
                if det_list:
                    all_detections.extend(det_list)
            left, right = self.strategy.decide(all_detections)
            if self.enabled:
                self.ws_client.send_command(left, right)
            time.sleep(self.decision_interval)

            #print(f"[DEBUG] Enriched detection {all_detections}", flush=True)

    def stop(self):
        self.running = False
        self.thread.join()
