# Changelog - Atualizações para Hardware Real

## ✅ Atualizações Realizadas

### 7. Versão 3.0 (Janeiro 2026) - Evolução Digital
- ✅ **Estrutura Modular:** Código movido para o pacote `bomb_app` com estados isolados.
- ✅ **State Machine:** Implementação de máquina de estados robusta (`state_machine.py`).
- ✅ **Modo Telegram (PIN Mode 3):** 
  - Integração total com bot do Telegram para alertas e defuse remoto.
  - Registro de usuários via ID do Telegram/Telefone.
- ✅ **PIN Dinâmico Evoluído (PIN Mode 2):**
  - Sistema de overlay transparente (80%) com logs de sistema ("software glitch").
  - Fake hacking effects na reveal do PIN.
- ✅ **Boot Video:** Suporte para carregamento e reprodução de vídeo de boot (`assets/boot_video.mp4`) usando OpenCV.
- ✅ **Reset Inteligente:** Long press em # (2s) agora retorna para a seleção de modo de PIN.
- ✅ **Hardware Mock:** Suporte para desenvolvimento/teste local sem hardware real (MockHW).
- ✅ **Refinamento de UI:** Ajustes de labels e inputs para melhor usabilidade ("PRESS # TO REGISTER", etc).

### 1. Display TFT SPI 240x320
- ✅ **display.py** completamente reescrito para suportar TFT SPI
- ✅ Suporte para controlador ST7789 (comum em displays 240x320)
- ✅ Interface compatível com código existente (LCDDisplay alias)
- ✅ Renderização usando PIL/Pillow para texto e gráficos
- ✅ Fallback para modo simulação se SPI não disponível

### 2. Keypad 4x3
- ✅ **config.py** atualizado com mapeamento correto para keypad 4x3
- ✅ KEYPAD_MAP ajustado para 12 teclas (1-9, 0, *, #)
- ✅ KEYPAD_COLS reduzido para 3 colunas (era 4)
- ✅ **bomb.py** configurado para usar keypad matricial por padrão

### 3. Configurações de Hardware
- ✅ **config.py** atualizado com pins corretos para TFT SPI:
  - RST: GPIO 25
  - DC: GPIO 24
  - CS: GPIO 8
  - MOSI/SCLK: Pins SPI padrão (GPIO 10/11)
- ✅ BUZZER_PIN alterado para GPIO 22 (evita conflito com TFT)

### 4. Dependências
- ✅ **requirements.txt** atualizado:
  - Removido: adafruit-circuitpython-lcd, adafruit-circuitpython-charlcd
  - Adicionado: Pillow, spidev
  - Mantido: RPi.GPIO

### 5. Scripts de Instalação
- ✅ **install.sh** atualizado:
  - Ativação automática de SPI
  - Instalação de python3-spidev e python3-pil
  - Verificação de necessidade de reinício
- ✅ **quick_setup.sh** criado:
  - Script de configuração rápida (mínimo de comandos)
  - Verifica e ativa SPI automaticamente
  - Instala todas as dependências

### 6. Documentação
- ✅ **HARDWARE_SETUP.md** completamente reescrito:
  - Conexões corretas para TFT SPI 240x320
  - Conexões para keypad 4x3
  - Diagramas atualizados
  - Troubleshooting específico para TFT SPI
- ✅ **SETUP_RASPBERRY.md** criado:
  - Guia completo de configuração inicial
  - Instruções passo a passo
  - Checklist de instalação
  - Comandos úteis
- ✅ **README.md** atualizado:
  - Componentes corretos listados
  - Instruções de instalação atualizadas
  - Referências aos novos documentos

## 📋 Checklist de Compatibilidade

### Hardware Suportado
- ✅ Display TFT SPI 240x320 (ST7789)
- ✅ Keypad matricial 4x3 (12 teclas)
- ✅ LEDs (GPIO)
- ✅ Buzzer (GPIO)
- ✅ Raspberry Pi 2 Model B ou superior

### Interfaces Ativadas
- ✅ SPI (obrigatório para display TFT)
- ✅ I2C (opcional, para outros componentes)
- ✅ GPIO (para keypad, LEDs, buzzer)

### Bibliotecas Python
- ✅ RPi.GPIO (controle GPIO)
- ✅ Pillow (renderização de imagens/texto)
- ✅ spidev (comunicação SPI)

## 🚀 Como Usar

### Configuração Mínima (Raspberry Pi já configurada)

```bash
# 1. Ativar SPI
sudo raspi-config
# Interface Options > SPI > Enable > Reboot

# 2. Após reiniciar, executar:
cd ~/AirsoftProject
chmod +x quick_setup.sh
./quick_setup.sh

# 3. Montar hardware (veja HARDWARE_SETUP.md)

# 4. Testar componentes
sudo python3 test_components.py

# 5. Executar
sudo python3 bomb.py
```

### Primeira Vez (Raspberry Pi Nova)

1. Siga o guia completo em `SETUP_RASPBERRY.md`
2. Execute `install.sh` ou `quick_setup.sh`
3. Monte o hardware conforme `HARDWARE_SETUP.md`
4. Teste e execute!

## ⚠️ Mudanças Importantes

### Pins Alterados
- **Buzzer:** GPIO 24 → GPIO 22 (para não conflitar com TFT DC)
- **Display:** Agora usa SPI (não I2C)
- **Keypad:** Agora 4x3 (não 4x4)

### Arquivos Modificados
- `display.py` - Reescrito completamente
- `config.py` - Pins e mapeamentos atualizados
- `bomb.py` - Keypad matricial por padrão
- `requirements.txt` - Bibliotecas atualizadas
- `install.sh` - SPI e novas dependências
- `HARDWARE_SETUP.md` - Documentação completa
- `README.md` - Informações atualizadas

### Arquivos Novos
- `SETUP_RASPBERRY.md` - Guia de configuração inicial
- `quick_setup.sh` - Script de configuração rápida
- `CHANGELOG.md` - Este arquivo

## 🔄 Compatibilidade com Versão Anterior

O código mantém compatibilidade de interface:
- `LCDDisplay` ainda funciona (alias para `TFTDisplay`)
- Métodos `print()`, `clear()`, `print_time()`, etc. mantidos
- `KeypadReader` funciona com ambos (matricial e USB)

## 📝 Notas

- O display TFT requer SPI ativado
- Keypad 4x3 tem 12 teclas (sem A, B, C, D)
- Todos os pins estão documentados em `HARDWARE_SETUP.md`
- Scripts de teste e instalação estão prontos para uso

---

**Data da Atualização:** 2024
**Versão:** 2.0 (Hardware Real)
