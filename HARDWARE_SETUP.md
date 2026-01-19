# Instruções de Montagem do Hardware

## Componentes do Projeto

- **Raspberry Pi 2 Model B** (ou superior)
- **Display TFT SPI 240x320** (3.2" TFT com controlador ST7789)
- **Keypad Matricial 4x3** (12 teclas: 1-9, 0, *, #)
- **LEDs** (mínimo 2, recomendado vermelhos)
- **Resistores 220Ω** (para LEDs)
- **Buzzer** (opcional)
- **Fios jumper**
- **Breadboard** (opcional, para testes)

## Diagrama de Conexões

### Pinout do Raspberry Pi (GPIO - 40 pins)

```
    3.3V  [1]  [2]  5V
   GPIO2  [3]  [4]  5V
   GPIO3  [5]  [6]  GND
   GPIO4  [7]  [8]  GPIO14
     GND  [9]  [10] GPIO15
  GPIO17 [11] [12] GPIO18  ← LED 1 / TFT Backlight
  GPIO27 [13] [14] GND
  GPIO22 [15] [16] GPIO23  ← LED 2
    3.3V [17] [18] GPIO24  ← TFT DC
  GPIO10 [19] [20] GND
   GPIO9 [21] [22] GPIO25  ← TFT RST
  GPIO11 [23] [24] GPIO8   ← TFT CS
     GND [25] [26] GPIO7
   GPIO0 [27] [28] GPIO1
   GPIO5 [29] [30] GND     ← Keypad Row 1
   GPIO6 [31] [32] GPIO12  ← Keypad Row 2
  GPIO13 [33] [34] GND     ← Keypad Row 3
  GPIO19 [35] [36] GPIO16  ← Keypad Row 4
  GPIO26 [37] [38] GPIO20  ← Keypad Col 1
     GND [39] [40] GPIO21  ← Keypad Col 2
                                    Keypad Col 3 → GPIO 26 (compartilhado)
```

## Conexões Detalhadas

### 1. Display TFT SPI 240x320

**Componente:** Display TFT 3.2" 240x320 com interface SPI

**Entradas do Display:**
VCC, GND, CS, RESET, DC, SDI (MOSI), SCK, LED, SDO (MISO), T_CLK, T_CS, T_DIN, T_DO, T_IRQ

**Conexões do Display (ligar estas):**
- **VCC** → Pin 2 (5V) - fio vermelho
- **GND** → Pin 6 (GND) - fio preto
- **CS** → Pin 24 (GPIO 8 / CE0)
- **RESET** → Pin 22 (GPIO 25)
- **DC** → Pin 18 (GPIO 24)
- **SDI (MOSI)** → Pin 19 (GPIO 10 / MOSI)
- **SCK** → Pin 23 (GPIO 11 / SCLK)
- **LED** → Pin 2 (5V) ou Pin 12 (GPIO 18) via resistor 220Ω

**Entradas que NÃO precisam ser ligadas (deixar desconectadas):**
- **SDO (MISO)** - não é necessário para este projeto
- **T_CLK, T_CS, T_DIN, T_DO, T_IRQ** - são para touchscreen, não são necessárias

**Nota:** 
- O display usa SPI, não I2C
- Verifique se o SPI está ativado: `lsmod | grep spi`
- Os pins SPI (MOSI, SCLK) são fixos no Raspberry Pi
- **Sempre ligue GND primeiro, depois VCC, depois os sinais**

### 2. LEDs

**Componentes necessários:**
- 2 LEDs vermelhos (ou mais)
- Resistores 220Ω (um para cada LED)

**Conexões LED 1:**
- **Anodo do LED** → Resistor 220Ω → Pin 12 (GPIO 18)
- **Cátodo do LED** → Pin 6 (GND)

**Conexões LED 2:**
- **Anodo do LED** → Resistor 220Ω → Pin 16 (GPIO 23)
- **Cátodo do LED** → Pin 6 (GND)

**Adicionar mais LEDs:**
- Adicione mais pins GPIO na lista `LED_PINS` em `config.py`
- Conecte cada LED com seu resistor 220Ω entre o GPIO e GND

### 3. Teclado Matricial 4x3

**Componente:** Teclado matricial 4x3 (12 teclas: 1-9, 0, *, #)

**Conexões:**
- **Linha 1 (Row 1)** → Pin 29 (GPIO 5)
- **Linha 2 (Row 2)** → Pin 31 (GPIO 6)
- **Linha 3 (Row 3)** → Pin 33 (GPIO 13)
- **Linha 4 (Row 4)** → Pin 35 (GPIO 19)
- **Coluna 1 (Col 1)** → Pin 37 (GPIO 26)
- **Coluna 2 (Col 2)** → Pin 38 (GPIO 20)
- **Coluna 3 (Col 3)** → Pin 40 (GPIO 21)

**Mapeamento das teclas:**
```
[1] [2] [3]
[4] [5] [6]
[7] [8] [9]
[*] [0] [#]
```

**Configuração:** No arquivo `bomb.py`, linha 30, use:
```python
self.keypad = KeypadReader(use_matrix=True)
```

**Alternativa - Teclado USB:**
Se preferir usar um teclado USB numérico (mais simples):
- Apenas conecte via USB
- No arquivo `bomb.py`, linha 30, use:
```python
self.keypad = KeypadReader(use_matrix=False)
```

### 4. Buzzer (Opcional)

**Componente:** Buzzer passivo ou ativo

**Conexões:**
- **Positivo** → Resistor 1kΩ → Pin 15 (GPIO 22)
- **Negativo** → Pin 6 (GND)

**Nota:** 
- Se usar buzzer ativo, pode não precisar do resistor. Teste primeiro sem resistor.
- O buzzer está configurado no GPIO 22 para não conflitar com o display TFT.

## Verificação das Conexões

### 1. Verificar SPI (Display TFT)
```bash
lsmod | grep spi
```
Deve mostrar módulos SPI carregados.

```bash
ls -l /dev/spi*
```
Deve mostrar dispositivos SPI (ex: /dev/spidev0.0).

### 2. Testar LEDs
```bash
sudo python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(18, GPIO.OUT); GPIO.output(18, GPIO.HIGH); import time; time.sleep(2); GPIO.output(18, GPIO.LOW); GPIO.cleanup()"
```
O LED conectado ao GPIO 18 deve acender por 2 segundos.

### 3. Testar Keypad
Execute o script de teste:
```bash
sudo python3 test_components.py
```
Escolha a opção de teclado matricial e teste as teclas.

### 4. Testar Display TFT
Execute o script de teste:
```bash
sudo python3 test_components.py
```
O display deve mostrar texto de teste.

## Dicas de Montagem

1. **Use uma breadboard** para facilitar as conexões durante testes
2. **Verifique a polaridade dos LEDs** - o anodo (perna longa) vai para o GPIO via resistor
3. **Use fios coloridos** para facilitar a identificação:
   - Vermelho = VCC/5V
   - Preto = GND
   - Amarelo = SPI (MOSI, SCLK)
   - Verde = GPIO de controle
   - Outras cores = GPIO de dados
4. **Teste cada componente separadamente** antes de conectar tudo
5. **Proteja o Raspberry Pi** - use uma caixa ou case para evitar curto-circuitos
6. **Verifique as especificações do display TFT** - alguns podem precisar de 3.3V, outros de 5V

## Troubleshooting

### Display TFT não funciona
- Verifique se o SPI está ativado: `sudo raspi-config` → Interface Options → SPI → Enable
- Verifique as conexões SPI (MOSI, SCLK, CS)
- Verifique se o display está recebendo energia (VCC e GND)
- Teste com: `sudo python3 -c "import spidev; spi = spidev.SpiDev(); spi.open(0, 0); print('SPI OK'); spi.close()"`
- Alguns displays TFT podem precisar de inicialização diferente - verifique o datasheet

### LEDs não acendem
- Verifique se os LEDs estão conectados corretamente (polaridade)
- Verifique se os resistores estão conectados
- Teste os GPIOs individualmente
- Verifique se não há conflito de pins (ex: GPIO 18 usado por LED e TFT backlight)

### Teclado não responde
- Verifique todas as conexões linha/coluna
- Verifique se os pins estão corretos em `config.py`
- Teste cada linha e coluna individualmente
- Verifique se não há curto-circuitos entre linhas/colunas

### Buzzer não faz som
- Verifique a polaridade
- Teste sem resistor primeiro (se buzzer ativo)
- Verifique se o GPIO está configurado corretamente
- Alguns buzzers precisam de PWM para diferentes frequências

### Conflitos de GPIO
- GPIO 18: Usado por LED 1 e pode ser usado por TFT backlight (escolha um)
- GPIO 24: Usado por TFT DC, não pode ser usado por outro componente
- GPIO 25: Usado por TFT RST, não pode ser usado por outro componente
- Verifique `config.py` para ver todos os pins em uso

## Diagrama Visual Simplificado

```
Raspberry Pi          Display TFT          Keypad 4x3
-----------          -----------          -----------
Pin 2 (5V)    ──────> VCC
Pin 6 (GND)   ──────> GND         ──────> GND (todas colunas)
Pin 19 (MOSI) ──────> MOSI/SDI
Pin 23 (SCLK) ──────> SCLK/SCK
Pin 24 (CS)   ──────> CS
Pin 18 (DC)   ──────> DC/A0
Pin 22 (RST)  ──────> RST

Pin 12 (GPIO18) ────> LED 1 (via resistor 220Ω)
Pin 16 (GPIO23) ────> LED 2 (via resistor 220Ω)

Pin 29 (GPIO5)  ────> Row 1
Pin 31 (GPIO6)  ────> Row 2
Pin 33 (GPIO13) ────> Row 3
Pin 35 (GPIO19) ────> Row 4
Pin 37 (GPIO26) ────> Col 1
Pin 38 (GPIO20) ────> Col 2
Pin 40 (GPIO21) ────> Col 3
```