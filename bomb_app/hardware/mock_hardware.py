from .interface import HardwareInterface
import time

class MockHardware(HardwareInterface):
    def __init__(self):
        self.held_keys = set()
        
    def initialize(self):
        print("[MockHW] Initialized")

    def cleanup(self):
        print("[MockHW] Cleanup")

    def set_led(self, led_name, state):
        # status = "ON" if state else "OFF"
        pass

    def beep(self, duration_ms):
        print(f"[MockHW] BEEP for {duration_ms}ms")

    def get_pressed_keys(self):
        return list(self.held_keys)

    def set_key_state(self, key, is_down):
        """Helper for PC simulation"""
        if is_down:
            self.held_keys.add(key)
        else:
            self.held_keys.discard(key)
