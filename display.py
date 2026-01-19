"""
Módulo para controlar o display TFT SPI 240x320
"""

import os
import time
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
from config import TFT_WIDTH, TFT_HEIGHT, TFT_PINS

try:
    import spidev
    SPI_AVAILABLE = True
except ImportError:
    SPI_AVAILABLE = False
    print("Aviso: spidev não disponível. Display funcionará em modo simulação.")

class TFTDisplay:
    """Classe para controlar display TFT SPI 240x320"""
    
    def __init__(self):
        self.width = TFT_WIDTH
        self.height = TFT_HEIGHT
        self.spi = None
        self.image = None
        self.draw = None
        self.font = None
        self._init_display()
    
    def _init_display(self):
        """Inicializa o display TFT"""
        try:
            # Limpar GPIOs antes de configurar (evita erro "gpio not allocated")
            try:
                GPIO.cleanup([TFT_PINS['RST'], TFT_PINS['DC'], TFT_PINS['CS']])
            except:
                pass
            
            # Configurar GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)  # Desabilitar avisos de GPIO já em uso
            
            # Configurar pins do display
            GPIO.setup(TFT_PINS['RST'], GPIO.OUT)
            GPIO.setup(TFT_PINS['DC'], GPIO.OUT)
            GPIO.setup(TFT_PINS['CS'], GPIO.OUT)
            
            # Inicializar pins
            GPIO.output(TFT_PINS['RST'], GPIO.HIGH)
            GPIO.output(TFT_PINS['DC'], GPIO.LOW)
            GPIO.output(TFT_PINS['CS'], GPIO.HIGH)
            
            if SPI_AVAILABLE:
                # Inicializar SPI
                self.spi = spidev.SpiDev()
                self.spi.open(0, 0)  # SPI bus 0, device 0
                self.spi.max_speed_hz = 32000000  # 32 MHz
                self.spi.mode = 0
                
                # Reset do display
                GPIO.output(TFT_PINS['RST'], GPIO.LOW)
                time.sleep(0.01)
                GPIO.output(TFT_PINS['RST'], GPIO.HIGH)
                time.sleep(0.12)
                
                # Inicializar display ST7789 (comum em TFT 240x320)
                self._init_st7789()
            
            # Criar imagem PIL para renderização
            self.image = Image.new('RGB', (self.width, self.height), color=(0, 0, 0))
            self.draw = ImageDraw.Draw(self.image)
            
            # Tentar carregar fonte, usar padrão se não disponível
            self.font = None
            self.font_small = None
            try:
                # Tentar fontes comuns do sistema
                font_paths = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                    "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans-Bold.ttf"
                ]
                for path in font_paths:
                    if os.path.exists(path):
                        self.font = ImageFont.truetype(path, 24)
                        self.font_small = ImageFont.truetype(path.replace("Bold", ""), 16)
                        break
            except:
                pass
            
            # Se não encontrou fonte, usar padrão
            if self.font is None:
                try:
                    self.font = ImageFont.load_default()
                    self.font_small = ImageFont.load_default()
                except:
                    pass
            
            print("Display TFT inicializado!")
            
        except Exception as e:
            print(f"Aviso: Não foi possível inicializar o display TFT: {e}")
            print("O programa continuará sem o display físico.")
            self.spi = None
    
    def _init_st7789(self):
        """Inicializa o controlador ST7789"""
        # Comandos de inicialização ST7789
        init_commands = [
            (0x01, None, 150),  # Software reset
            (0x11, None, 120),  # Exit sleep
            (0x3A, [0x55], 0),  # Pixel format: 16-bit color
            (0x36, [0x00], 0),  # Memory access control
            (0x29, None, 0),    # Display on
        ]
        
        for cmd, data, delay in init_commands:
            self._write_command(cmd)
            if data:
                for d in data:
                    self._write_data(d)
            if delay:
                time.sleep(delay / 1000.0)
    
    def _write_command(self, cmd):
        """Envia comando para o display"""
        if self.spi is None:
            return
        
        GPIO.output(TFT_PINS['DC'], GPIO.LOW)  # Comando
        GPIO.output(TFT_PINS['CS'], GPIO.LOW)
        self.spi.xfer2([cmd])
        GPIO.output(TFT_PINS['CS'], GPIO.HIGH)
    
    def _write_data(self, data):
        """Envia dado para o display"""
        if self.spi is None:
            return
        
        GPIO.output(TFT_PINS['DC'], GPIO.HIGH)  # Dado
        GPIO.output(TFT_PINS['CS'], GPIO.LOW)
        if isinstance(data, list):
            self.spi.xfer2(data)
        else:
            self.spi.xfer2([data])
        GPIO.output(TFT_PINS['CS'], GPIO.HIGH)
    
    def _set_window(self, x0, y0, x1, y1):
        """Define janela de escrita"""
        self._write_command(0x2A)  # Column address set
        self._write_data([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF])
        self._write_command(0x2B)  # Row address set
        self._write_data([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF])
        self._write_command(0x2C)  # Memory write
    
    def _update_display(self):
        """Atualiza o display físico com a imagem PIL"""
        if self.spi is None:
            return
        
        # Converter imagem PIL para bytes RGB565
        pixels = self.image.convert('RGB').load()
        self._set_window(0, 0, self.width - 1, self.height - 1)
        
        # Enviar pixels (RGB565 format)
        pixel_data = []
        for y in range(self.height):
            for x in range(self.width):
                r, g, b = pixels[x, y]
                # Converter RGB888 para RGB565
                pixel = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                pixel_data.append(pixel >> 8)
                pixel_data.append(pixel & 0xFF)
        
        # Enviar em chunks para não sobrecarregar
        chunk_size = 4096
        for i in range(0, len(pixel_data), chunk_size):
            self._write_data(pixel_data[i:i+chunk_size])
    
    def clear(self):
        """Limpa o display"""
        if self.draw:
            self.draw.rectangle([(0, 0), (self.width, self.height)], fill=(0, 0, 0))
            self._update_display()
        else:
            print("[DISPLAY] Limpo")
    
    def set_cursor(self, row, col):
        """Define posição do cursor (compatibilidade com interface antiga)"""
        # Para TFT, não precisamos de cursor, mas mantemos para compatibilidade
        pass
    
    def print(self, text, row=0, col=0):
        """Imprime texto no display"""
        if self.draw is None:
            print(f"[DISPLAY Linha {row}]: {text}")
            return
        
        # Calcular posição Y baseada na linha (aproximadamente 30px por linha)
        y = row * 30 + 10
        x = col * 8 + 10
        
        # Limpar área do texto primeiro
        text_width = len(text) * 12
        text_height = 25
        self.draw.rectangle([(x, y), (x + text_width, y + text_height)], fill=(0, 0, 0))
        
        # Desenhar texto
        font_to_use = self.font if len(text) < 20 else self.font_small
        self.draw.text((x, y), text, fill=(255, 255, 255), font=font_to_use)
        self._update_display()
    
    def print_time(self, seconds):
        """Imprime tempo formatado (MM:SS)"""
        minutes = seconds // 60
        secs = seconds % 60
        time_str = f"{minutes:02d}:{secs:02d}"
        # Centralizar no display
        x = (self.width - len(time_str) * 20) // 2
        self.print(time_str, 0, x // 8)
    
    def print_status(self, status):
        """Imprime status na segunda linha"""
        x = (self.width - len(status) * 12) // 2
        self.print(status, 1, x // 8)
    
    def close(self):
        """Fecha a conexão"""
        if self.spi:
            self.clear()
            self.spi.close()
        GPIO.cleanup([TFT_PINS['RST'], TFT_PINS['DC'], TFT_PINS['CS']])


# Alias para compatibilidade com código existente
LCDDisplay = TFTDisplay
