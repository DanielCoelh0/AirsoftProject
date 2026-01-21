from abc import ABC, abstractmethod

class HardwareInterface(ABC):
    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass

    @abstractmethod
    def set_led(self, led_name, state):
        """Turn LED on (True) or off (False). led_name: 'RED', 'GREEN'"""
        pass

    @abstractmethod
    def beep(self, duration_ms):
        pass

    @abstractmethod
    def get_pressed_keys(self):
        """Return a list of keys currently being held down. Keys: '0'-'9', '*', '#'"""
        pass
