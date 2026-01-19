"""
Módulo para controlar os LEDs
"""

import RPi.GPIO as GPIO
import threading
import time
from config import LED_PINS, LED_BLINK_INTERVAL

class LEDController:
    """Classe para controlar LEDs piscando"""
    
    def __init__(self):
        self.led_pins = LED_PINS
        self.blink_interval = LED_BLINK_INTERVAL
        self.is_blinking = False
        self.blink_thread = None
        self._init_gpio()
    
    def _init_gpio(self):
        """Inicializa os GPIOs"""
        # GPIO.setmode já foi chamado no bomb.py, não precisa chamar novamente
        for pin in self.led_pins:
            try:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.LOW)
            except RuntimeError as e:
                # Se GPIO já estiver configurado, tenta limpar e reconfigurar
                try:
                    GPIO.cleanup(pin)
                    GPIO.setup(pin, GPIO.OUT)
                    GPIO.output(pin, GPIO.LOW)
                except:
                    print(f"Aviso: Não foi possível configurar GPIO {pin} para LED")
    
    def _blink_loop(self):
        """Loop para piscar os LEDs"""
        state = False
        while self.is_blinking:
            for pin in self.led_pins:
                GPIO.output(pin, GPIO.HIGH if state else GPIO.LOW)
            state = not state
            time.sleep(self.blink_interval)
    
    def start_blinking(self):
        """Inicia o piscar dos LEDs"""
        if not self.is_blinking:
            self.is_blinking = True
            self.blink_thread = threading.Thread(target=self._blink_loop, daemon=True)
            self.blink_thread.start()
    
    def stop_blinking(self):
        """Para o piscar dos LEDs"""
        self.is_blinking = False
        if self.blink_thread:
            self.blink_thread.join(timeout=1)
        # Desligar todos os LEDs
        for pin in self.led_pins:
            GPIO.output(pin, GPIO.LOW)
    
    def turn_on(self):
        """Liga todos os LEDs"""
        self.stop_blinking()
        for pin in self.led_pins:
            GPIO.output(pin, GPIO.HIGH)
    
    def turn_off(self):
        """Desliga todos os LEDs"""
        self.stop_blinking()
        for pin in self.led_pins:
            GPIO.output(pin, GPIO.LOW)
    
    def cleanup(self):
        """Limpa os GPIOs"""
        self.stop_blinking()
        for pin in self.led_pins:
            GPIO.setup(pin, GPIO.IN)
