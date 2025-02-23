#!/bin/bash
set -e

# System setup
sudo apt update && sudo apt full-upgrade -y
sudo raspi-config nonint do_memory_split 512  # Required for Hailo-8 DMA
sudo apt install -y \
    python3-pip \
    python3-venv \
    i2c-tools \
    libatlas-base-dev \
    libopenjp2-7 \
    libtiff5

# Add Hailo repository
echo "deb https://hailo.ai/apt/$(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hailo.list
curl -sSL https://hailo.ai/apt/hailo.gpg | sudo apt-key add -

# Install Hailo packages
sudo apt update && sudo apt install -y \
    hailo-platform \
    hailo-post-processes \
    hailo-model-zoo \
    hailo-tappas \
    hailo8-firmware

# Add udev rule for Hailo-8
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="03e7", MODE="0666"' | sudo tee /etc/udev/rules.d/99-hailo8.rules
sudo udevadm control --reload

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Configure services
sudo tee /etc/systemd/system/pan-tilt.service <<EOL
[Unit]
Description=Pan-Tilt Tracking System
After=network.target

[Service]
User=pi
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/venv/bin/python -m tracker.web_ui
Environment=LD_LIBRARY_PATH=/opt/hailo/hailo_sw_suite/lib
Environment=HAILO_DEFAULT_DEVICE_TYPE=HAILO8
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

echo "Installation complete! Start with:"
echo "sudo systemctl enable --now pan-tilt.service" 