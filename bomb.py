#!/usr/bin/env python3
"""
Bomba Simulada para Airsoft
Programa principal que controla a simulação da bomba
"""

import RPi.GPIO as GPIO
import time
import signal
import sys
from config import CORRECT_CODE, INITIAL_TIME, CODE_ENTRY_TIMEOUT, DISPLAY_UPDATE_INTERVAL, BUZZER_PIN
from display import LCDDisplay
from leds import LEDController
from keypad import KeypadReader

class BombSimulator:
    """Classe principal para simular a bomba"""
    
    def __init__(self):
        self.correct_code = CORRECT_CODE
        self.time_remaining = INITIAL_TIME
        self.is_active = False
        self.is_defused = False
        self.is_exploded = False
        
        # Limpar GPIOs antes de inicializar (evita erro "gpio not allocated")
        try:
            GPIO.cleanup()
        except:
            pass
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Inicializar componentes
        print("Inicializando componentes...")
        self.display = LCDDisplay()
        self.leds = LEDController()
        self.keypad = KeypadReader(use_matrix=True)  # Keypad matricial 4x3 (mude para False se usar USB)
        
        # Inicializar buzzer (opcional)
        try:
            GPIO.setup(BUZZER_PIN, GPIO.OUT)
            self.has_buzzer = True
        except:
            self.has_buzzer = False
        
        # Configurar handler para Ctrl+C
        signal.signal(signal.SIGINT, self._signal_handler)
        
        print("Componentes inicializados!")
    
    def _signal_handler(self, sig, frame):
        """Handler para interrupção (Ctrl+C)"""
        print("\n\nInterrompendo bomba...")
        self.cleanup()
        sys.exit(0)
    
    def _beep(self, duration=0.1, frequency=1000):
        """Toca um beep no buzzer"""
        if not self.has_buzzer:
            return
        
        # Buzzer passivo simples - apenas liga/desliga
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        time.sleep(duration)
        GPIO.output(BUZZER_PIN, GPIO.LOW)
    
    def _format_time(self, seconds):
        """Formata tempo em MM:SS"""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
    
    def _update_display(self):
        """Atualiza o display com informações atuais"""
        if self.is_defused:
            self.display.print("BOMBA", 0, 5)
            self.display.print("DESATIVADA!", 1, 3)
        elif self.is_exploded:
            self.display.print("***EXPLOSAO***", 0, 1)
            self.display.print("***BOOM***", 1, 3)
        elif self.is_active:
            time_str = self._format_time(self.time_remaining)
            self.display.print(f"TEMPO: {time_str}", 0, 0)
            self.display.print("DIGITE CODIGO!", 1, 0)
        else:
            self.display.print("BOMBA SIMULADA", 0, 1)
            self.display.print("PRONTA", 1, 5)
    
    def _check_code(self, code):
        """Verifica se o código está correto"""
        return code == self.correct_code
    
    def _explode(self):
        """Simula explosão"""
        self.is_exploded = True
        self.is_active = False
        self.leds.turn_on()
        
        # Sequência de beeps
        for _ in range(5):
            self._beep(0.2, 1000)
            time.sleep(0.1)
        
        self.display.clear()
        self._update_display()
        
        print("\n" + "="*50)
        print("*** EXPLOSÃO SIMULADA ***")
        print("="*50)
        time.sleep(3)
    
    def _defuse(self):
        """Desativa a bomba"""
        self.is_defused = True
        self.is_active = False
        self.leds.stop_blinking()
        self.leds.turn_off()
        
        # Beep de sucesso
        for _ in range(3):
            self._beep(0.1, 1500)
            time.sleep(0.1)
        
        self.display.clear()
        self._update_display()
        
        print("\n" + "="*50)
        print("*** BOMBA DESATIVADA COM SUCESSO! ***")
        print("="*50)
        time.sleep(5)
    
    def start(self):
        """Inicia a bomba"""
        print("\n" + "="*50)
        print("BOMBA SIMULADA PARA AIRSOFT")
        print("="*50)
        print(f"Código correto: {self.correct_code}")
        print(f"Tempo inicial: {self._format_time(INITIAL_TIME)}")
        print("\nPressione ENTER para ativar a bomba...")
        
        input()
        
        self.is_active = True
        self.time_remaining = INITIAL_TIME
        self.leds.start_blinking()
        
        print("\n*** BOMBA ATIVADA! ***")
        print("Digite o código para desativar!")
        
        start_time = time.time()
        last_display_update = 0
        
        # Loop principal
        while self.is_active and not self.is_defused and not self.is_exploded:
            current_time = time.time()
            elapsed = current_time - start_time
            self.time_remaining = max(0, INITIAL_TIME - int(elapsed))
            
            # Atualizar display periodicamente
            if current_time - last_display_update >= DISPLAY_UPDATE_INTERVAL:
                self._update_display()
                last_display_update = current_time
            
            # Verificar se o tempo acabou
            if self.time_remaining <= 0:
                self._explode()
                break
            
            # Tentar ler código do teclado (não bloqueante)
            key = self.keypad.get_key()
            
            if key and key.isdigit():
                # Iniciar entrada de código
                print(f"\nInserindo código... (Tempo restante: {self._format_time(self.time_remaining)})")
                entered_code = self.keypad.get_code(max_digits=len(self.correct_code), 
                                                   timeout=CODE_ENTRY_TIMEOUT)
                
                if entered_code:
                    if self._check_code(entered_code):
                        self._defuse()
                        break
                    else:
                        print("Código incorreto! Tente novamente.")
                        self.display.print("CODIGO ERRADO!", 1, 0)
                        time.sleep(2)
                        self._update_display()
                        # Beep de erro
                        self._beep(0.3, 500)
            
            # Beep de alerta quando tempo está acabando
            if self.time_remaining <= 30 and self.time_remaining % 5 == 0:
                self._beep(0.05, 2000)
            
            time.sleep(0.1)
        
        # Manter display atualizado após o fim
        while True:
            self._update_display()
            time.sleep(1)
    
    def cleanup(self):
        """Limpa recursos e desliga componentes"""
        print("\nLimpando recursos...")
        self.leds.cleanup()
        self.display.close()
        self.keypad.cleanup()
        GPIO.cleanup()
        print("Recursos limpos.")

def main():
    """Função principal"""
    try:
        bomb = BombSimulator()
        bomb.start()
    except KeyboardInterrupt:
        print("\n\nInterrompido pelo usuário.")
    except Exception as e:
        print(f"\nErro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'bomb' in locals():
            bomb.cleanup()

if __name__ == "__main__":
    main()
