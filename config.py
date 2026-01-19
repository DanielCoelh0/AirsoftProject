"""
Configurações para a bomba simulada de airsoft
"""

# Código correto para desativar a bomba (4 dígitos)
CORRECT_CODE = "1234"

# Tempo inicial em segundos
INITIAL_TIME = 300  # 5 minutos

# Configurações do Display TFT SPI 240x320
TFT_WIDTH = 240
TFT_HEIGHT = 320
# Pins do display TFT SPI
TFT_PINS = {
    'RST': 25,   # GPIO 25 - Reset
    'DC': 24,    # GPIO 24 - Data/Command
    'CS': 8,     # GPIO 8 - Chip Select (CE0)
    'MOSI': 10,  # GPIO 10 - MOSI (SPI)
    'SCLK': 11,  # GPIO 11 - SCLK (SPI)
    'LED': 18    # GPIO 18 - Backlight (opcional, pode usar VCC)
}

# Configurações dos LEDs
# NOTA: GPIO 18 removido porque é usado pelo display TFT backlight
LED_PINS = [23]  # GPIO pins para os LEDs (GPIO 18 usado pelo display)
LED_BLINK_INTERVAL = 0.5  # Intervalo de piscar em segundos

# Configurações do Teclado Matricial 4x3
# Keypad 4x3 (12 teclas: 1-9, 0, *, #)
KEYPAD_ROWS = [5, 6, 13, 19]  # GPIO pins para linhas (4 linhas)
KEYPAD_COLS = [26, 20, 21]    # GPIO pins para colunas (3 colunas)

# Mapeamento do teclado matricial 4x3
KEYPAD_MAP = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
    ['*', '0', '#']
]

# Buzzer (opcional)
BUZZER_PIN = 22  # GPIO pin para buzzer (alterado para não conflitar com TFT)

# Configurações de timing
CODE_ENTRY_TIMEOUT = 30  # Tempo máximo para inserir código (segundos)
DISPLAY_UPDATE_INTERVAL = 0.1  # Intervalo de atualização do display (segundos)
