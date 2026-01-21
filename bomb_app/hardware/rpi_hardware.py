from .interface import HardwareInterface
try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None
import time
from .. import config

class RpiHardware(HardwareInterface):
    def __init__(self):
        self.rows = [config.PIN_ROW_1, config.PIN_ROW_2, config.PIN_ROW_3, config.PIN_ROW_4]
        self.cols = [config.PIN_COL_1, config.PIN_COL_2, config.PIN_COL_3]
        self.matrix = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['*', '0', '#']
        ]
        
    def initialize(self):
        if GPIO is None:
            print("RPi.GPIO not found. Hardware will not work.")
            return
            
        GPIO.setmode(GPIO.BCM)
        
        # LEDs
        GPIO.setup(config.PIN_LED_RED, GPIO.OUT)
        GPIO.setup(config.PIN_LED_GREEN, GPIO.OUT)
        GPIO.setup(config.PIN_BUZZER, GPIO.OUT)  # Active buzzer?
        
        # Keypad
        for col in self.cols:
            GPIO.setup(col, GPIO.OUT)
            GPIO.output(col, 1)
            
        for row in self.rows:
            GPIO.setup(row, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def cleanup(self):
        if GPIO:
            GPIO.cleanup()

    def set_led(self, led_name, state):
        if GPIO is None: return
        pin = config.PIN_LED_RED if led_name == 'RED' else config.PIN_LED_GREEN
        GPIO.output(pin, 1 if state else 0)

    def beep(self, duration_ms):
        if GPIO is None: return
        GPIO.output(config.PIN_BUZZER, 1)
        # Note: This is blocking, might want to make it non-blocking in a real loop
        # For now, simplistic.
        time.sleep(duration_ms / 1000.0)
        GPIO.output(config.PIN_BUZZER, 0)

    def get_pressed_keys(self):
        if GPIO is None: return []
        
        pressed = []
        for j, col in enumerate(self.cols):
            GPIO.output(col, 1)
            for i, row in enumerate(self.rows):
                if GPIO.input(row) == 1:
                    pressed.append(self.matrix[i][j])
            GPIO.output(col, 0)
        return pressed
