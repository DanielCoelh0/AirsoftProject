# Bomba Simulada para Airsoft 🎯 (Versão 3.0)

Projeto para criar uma bomba simulada (NÃO REAL) para jogos de airsoft usando Raspberry Pi, com integração Telegram e modos avançados de PIN.

## ⚠️ AVISO IMPORTANTE
Este projeto é apenas para simulação e jogos de airsoft. NÃO é uma bomba real e não deve ser usado de forma a causar alarme ou confusão em locais públicos.

## ✨ Funcionalidades Avançadas
- 🎮 **3 Modos de Operação**:
  1. **Static PIN**: Código fixo configurado no sistema.
  2. **Dynamic PIN**: Código definido pelo Terrorista no plant, revelado ao Contra-Terrorista via "Software Glitch" após validação de telefone.
  3. **Telegram Dynamic**: Igual ao dinâmico, mas envia o código revelado diretamente para o bot do Telegram.
- 📱 **Integração Telegram**: Receba alertas de plant e códigos de defuse no seu celular.
- 📺 **Visual Premium**: Interface com efeitos de transparência, sistema de logs estilo hacking e vídeo de boot customizado.
- ⏱️ **Timer Preciso**: Timer com milissegundos e beeps progressivos.
- 🔌 **Hardware Robusto**: Suporte para Display TFT ST7789, Teclado 4x3 e Buzzers.

## 📐 Estrutura do Projeto
```
AirsoftProject/
├── main.py                # Ponto de entrada do programa
├── bomb_app/
│   ├── state_machine.py   # Lógica central e estados do jogo
│   ├── telegram_service.py # Integração com Bot API
│   ├── config.py          # Configurações de hardware e tempos
│   ├── hardware/          # Abstração de hardware (Real vs Mock)
│   ├── ui/
│   │   └── renderer.py    # Sistema de renderização Pygame
│   └── assets/            # Vídeos e mídias
├── changelog.md           # Histórico de versões
└── hardware_setup.md      # Guia de pinagem e eletrônica
```

## 🚀 Como Iniciar

1. **Configure o Bot do Telegram**: Edite `bomb_app/telegram_config.py` com seu Token e IDs de chat.
2. **Instale as dependências**:
   ```bash
   pip install pygame-ce opencv-python pillow python-telegram-bot
   ```
3. **Executar**:
   ```bash
   python main.py
   ```

## ⌨️ Comandos Globais
- **Segurar # (2 segundos)**: Reinicia o jogo e volta para a seleção de modo de PIN.
- **Pressionar * (na tela READY)**: Inicia a fase de plant.
- **Pressionar * (nas fases de jogo)**: Abre o campo para inserção de código.

## 🔧 Configuração
Ajuste os tempos padrão e pinagem em `bomb_app/config.py`.

---
**Desenvolvido para jogos de airsoft - Use com responsabilidade! 🎮**
