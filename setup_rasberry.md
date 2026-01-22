# Guia de Configuração Inicial da Raspberry Pi

Este guia ajuda você a configurar a Raspberry Pi do zero para rodar o projeto da bomba simulada.

## 📤 Preparar o Projeto para GitHub (Opcional - Mas Recomendado)

Se ainda não colocou o projeto no GitHub, siga estes passos:

1. **Criar repositório no GitHub:**
   - Acesse: https://github.com/new
   - Nome: `AirsoftProject` (ou outro nome)
   - Escolha público ou privado
   - **NÃO** inicialize com README, .gitignore ou licença
   - Clique em "Create repository"

2. **No seu computador, no diretório do projeto:**
   ```bash
   cd /caminho/para/AirsoftProject
   git remote add origin https://github.com/SEU_USERNAME/AirsoftProject.git
   git branch -M main
   git push -u origin main
   ```

   **Substitua `SEU_USERNAME` pelo seu username do GitHub.**

3. **Depois, na Raspberry Pi, pode clonar diretamente:**
   ```bash
   cd ~
   git clone https://github.com/SEU_USERNAME/AirsoftProject.git
   ```

## 📋 Pré-requisitos

- Raspberry Pi 2 Model B (ou superior)
- Cartão microSD (mínimo 8GB, recomendado 16GB+)
- Fonte de alimentação adequada (5V, mínimo 2A)
- Cabo HDMI (para monitor, opcional)
- Teclado e mouse USB (ou acesso SSH)
- Computador para gravar a imagem no cartão SD
- **Cabo Ethernet** (para conexão à internet)

## 🚀 Passo 1: Instalar o Sistema Operativo

### Opção A: Raspberry Pi Imager (Recomendado - Mais Fácil)

1. **Baixar Raspberry Pi Imager:**
   - Acesse: https://www.raspberrypi.com/software/
   - Baixe e instale o Raspberry Pi Imager no seu computador

2. **Gravar a imagem:**
   - Abra o Raspberry Pi Imager
   - Clique em "Choose OS"
   - Selecione "Raspberry Pi OS (Lite)" - versão sem interface gráfica (mais leve)
     - OU "Raspberry Pi OS (32-bit)" - versão com interface gráfica
   - Clique em "Choose Storage" e selecione seu cartão microSD
   - Clique em "Write" e aguarde a gravação

3. **Configurar antes de gravar (Opcional):**
   - No Raspberry Pi Imager, clique no ícone de engrenagem (⚙️)
   - Configure:
     - Hostname: `airsoft-bomb` (ou outro nome)
     - SSH: Ative e defina usuário/senha
     - Localização: Configure timezone e layout de teclado

### Opção B: Download Manual da Imagem

1. **Baixar imagem:**
   - Acesse: https://www.raspberrypi.org/downloads/
   - Baixe "Raspberry Pi OS Lite" (sem interface gráfica) ou "Raspberry Pi OS" (com interface)

2. **Gravar no cartão SD:**
   - Use ferramentas como:
     - **Windows:** Win32DiskImager, Balena Etcher
     - **Mac:** Balena Etcher
     - **Linux:** `dd` command ou Balena Etcher

## 🔌 Passo 2: Primeira Inicialização

### Se usar Interface Gráfica (Desktop):

1. Insira o cartão SD na Raspberry Pi
2. Conecte monitor, teclado, mouse e fonte
3. Conecte cabo Ethernet
4. Ligue a Raspberry Pi
5. Aguarde a inicialização (pode demorar alguns minutos na primeira vez)
6. Siga as instruções de configuração inicial

### Se usar Lite (Linha de Comando):

1. Insira o cartão SD na Raspberry Pi
2. Conecte cabo de rede (Ethernet)
3. Conecte fonte e ligue
4. Acesse via SSH:
   ```bash
   ssh pi@raspberrypi.local
   # ou
   ssh pi@<IP_DA_RASPBERRY>
   ```
   - Usuário padrão: `pi`
   - Senha padrão: `raspberry` (mude imediatamente!)

## ⚙️ Passo 3: Configuração Básica do Sistema

### 3.1 Atualizar o Sistema

Com o cabo Ethernet conectado, atualize o sistema:

```bash
sudo apt update
sudo apt upgrade -y
```

### 3.2 Configurar Raspberry Pi (raspi-config)

```bash
sudo raspi-config
```

**Configurações importantes:**

1. **System Options → Password:** Mude a senha do usuário `pi`
2. **System Options → Hostname:** Altere para `airsoft-bomb` (opcional)
3. **Interface Options → SPI:** **Enable** (OBRIGATÓRIO para display TFT)
4. **Interface Options → I2C:** Enable (opcional, para outros componentes)
5. **Localisation Options → Change Locale:** Selecione `en_US.UTF-8` ou `pt_PT.UTF-8`
6. **Localisation Options → Change Timezone:** Configure seu fuso horário
7. **Advanced Options → Expand Filesystem:** Execute para usar todo o espaço do cartão SD

**Salve e reinicie quando solicitado:**
```bash
sudo reboot
```

### 3.3 Verificar Interfaces Ativadas

Após reiniciar, verifique se SPI está ativo:

```bash
# Verificar SPI
lsmod | grep spi
ls -l /dev/spi*

# Deve mostrar algo como:
# /dev/spidev0.0
# /dev/spidev0.1
```

## 📦 Passo 4: Instalar o Projeto

### 4.1 Transferir Arquivos para a Raspberry Pi

**Opção A: Via Git/GitHub (Recomendado - Mais Fácil):**

Se o projeto estiver no GitHub:

```bash
cd ~
git clone https://github.com/SEU_USERNAME/AirsoftProject.git
cd AirsoftProject
```

**Substitua `SEU_USERNAME` pelo seu username do GitHub.**

**Exemplo:**
```bash
cd ~
git clone https://github.com/danielcoelho/AirsoftProject.git
cd AirsoftProject
```

**Opção B: Via SCP (do seu computador):**
```bash
# No seu computador (não na Raspberry Pi):
scp -r /caminho/para/AirsoftProject pi@raspberrypi.local:~/
```

**Opção C: Via USB/Network Share:**
- Copie os arquivos via USB ou compartilhamento de rede

### 4.2 Configurar Bot do Telegram (Opcional - Para PIN Mode 3)

1. Crie um bot via [@BotFather](https://t.me/botfather) e obtenha o `TOKEN`.
2. Obtenha seu `CHAT_ID` via [@userinfobot](https://t.me/userinfobot).
3. Edite o arquivo de configuração:
   ```bash
   nano bomb_app/telegram_config.py
   ```
   Insira seu Token e os IDs de chat para Terroristas e Contra-Terroristas.

### 4.3 Instalar Dependências

```bash
pip3 install pygame-ce opencv-python pillow python-telegram-bot
```

## 🧪 Passo 5: Testar Componentes

Após reiniciar e montar o hardware:

```bash
cd ~/AirsoftProject
sudo python3 test_components.py
```

Teste cada componente individualmente:
- LEDs
- Display TFT
- Keypad
- Buzzer (se conectado)

## 🎮 Passo 6: Executar o Projeto

```bash
cd ~/AirsoftProject
python main.py
```

**Nota:** O `sudo` pode ser necessário para acessar GPIOs, dependendo da configuração.

## 🔧 Comandos Úteis

### Verificar Status do Sistema
```bash
# Verificar temperatura
vcgencmd measure_temp

# Verificar uso de memória
free -h

# Verificar espaço em disco
df -h
```

### Verificar Interfaces
```bash
# Verificar SPI
lsmod | grep spi
ls -l /dev/spi*

# Verificar I2C
lsmod | grep i2c
i2cdetect -y 1
```

### Atualizar Sistema
```bash
sudo apt update
sudo apt upgrade -y
```

### Reiniciar/Desligar
```bash
sudo reboot
sudo shutdown -h now
```

## 🐛 Troubleshooting

### Problema: Não consigo acessar via SSH
- Verifique se SSH está ativado: `sudo systemctl enable ssh`
- Verifique o IP: `hostname -I`
- Verifique firewall: `sudo ufw status`

### Problema: SPI não funciona
- Verifique se está ativado: `sudo raspi-config` → Interface Options → SPI
- Verifique se reiniciou após ativar
- Verifique módulos: `lsmod | grep spi`

### Problema: Permissões GPIO
- Execute com `sudo`: `sudo python3 bomb.py`
- OU adicione usuário ao grupo gpio: `sudo usermod -a -G gpio pi`

### Problema: Display não funciona
- Verifique conexões SPI (MOSI, SCLK, CS, DC, RST)
- Verifique se SPI está ativo: `ls -l /dev/spi*`
- Verifique alimentação (VCC e GND)
- Teste com script de teste: `sudo python3 test_components.py`

## 📝 Checklist Rápido

- [ ] Sistema operativo instalado no cartão SD
- [ ] Raspberry Pi inicializada e configurada
- [ ] SPI ativado via `raspi-config`
- [ ] Sistema atualizado (`sudo apt update && sudo apt upgrade`)
- [ ] Projeto copiado para a Raspberry Pi
- [ ] Script `install.sh` executado com sucesso
- [ ] Sistema reiniciado (se necessário)
- [ ] Hardware montado conforme `HARDWARE_SETUP.md`
- [ ] Componentes testados com `test_components.py`
- [ ] Projeto executado com sucesso: `sudo python3 bomb.py`

## 🎯 Configuração Mínima (Comandos Essenciais)

Se você já tem a Raspberry Pi configurada e só quer instalar o projeto:

```bash
# 1. Ativar SPI
sudo raspi-config
# Interface Options → SPI → Enable → Reboot

# 2. Após reiniciar, instalar dependências
sudo apt update
sudo apt install -y python3-pip python3-dev python3-spidev python3-pil

# 3. Instalar bibliotecas Python
pip3 install --user RPi.GPIO Pillow spidev

# 4. Executar projeto
cd ~/AirsoftProject
python main.py
```

## 📞 Suporte

Se encontrar problemas:
1. Verifique `HARDWARE_SETUP.md` para conexões
2. Execute `test_components.py` para testar individualmente
3. Verifique logs de erro no terminal
4. Verifique se todos os pins estão corretos em `config.py`
