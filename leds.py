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
        # Garantir que GPIO está configurado
        try:
            GPIO.setmode(GPIO.BCM)
        except:
            pass
        
        GPIO.setwarnings(False)
        
        # Configurar cada pin como OUTPUT
        for pin in self.led_pins:
            try:
                # Primeiro configurar como input (modo seguro)
                try:
                    GPIO.setup(pin, GPIO.IN)
                except:
                    pass
                # Depois configurar como output
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.LOW)
            except Exception as e:
                print(f"Aviso: Não foi possível configurar GPIO {pin} para LED: {e}")
    
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
        # Desligar todos os LEDs (com verificação de segurança)
        for pin in self.led_pins:
            try:
                # Verificar se o pin está configurado antes de usar
                GPIO.output(pin, GPIO.LOW)
            except RuntimeError:
                # Se não estiver configurado, tentar configurar primeiro
                try:
                    GPIO.setup(pin, GPIO.OUT)
                    GPIO.output(pin, GPIO.LOW)
                except:
                    pass
            except:
                pass
    
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
        try:
            self.stop_blinking()
        except:
            pass
        
        # Configurar pins como input (modo seguro)
        for pin in self.led_pins:
            try:
                GPIO.setup(pin, GPIO.IN)
            except:
                pass
