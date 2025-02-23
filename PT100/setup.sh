#!/bin/bash

# System update and base dependencies
sudo apt update && sudo apt full-upgrade -y
sudo apt install -y \
    python3-pip \
    python3-opencv \
    libhailort \
    i2c-tools \
    git \
    build-essential \
    libatlas-base-dev \
    libopenjp2-7 \
    libtiff5 \
    libgl1

# Enable hardware interfaces
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_camera 0
sudo raspi-config nonint do_memory_split 256

# Install Python dependencies
pip3 install --upgrade pip
pip3 install \
    gpiozero \
    icm20948-python \
    numpy \
    picamera2 \
    smbus2 \
    pyyaml \
    adafruit-circuitpython-servokit \
    flask \
    flask-socketio \
    eventlet \
    psutil \
    matplotlib

# Hailo AI setup
wget https://hailo.ai/developers/rpi/rpi5/hailort_5.0.0_arm64.deb  # Check latest URL
sudo dpkg -i hailort_*.deb
sudo apt-get install -f -y
rm hailort_*.deb

# Clone required repositories
mkdir -p ~/projects && cd ~/projects
git clone https://github.com/hailo-ai/hailo_model_zoo.git
git clone https://github.com/hailo-ai/hailo-rpi5-examples.git
git clone https://github.com/pimoroni/icm20948-python.git

# Configure udev rules for Hailo
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="03e7", MODE="0666"' | sudo tee /etc/udev/rules.d/80-hailo.rules
sudo udevadm control --reload-rules

# Create project structure
mkdir -p ~/pan_tilt_tracker/{models,configs,logs}

# Set up environment variables
echo "export PYTHONPATH=\$PYTHONPATH:~/projects/hailo_model_zoo" >> ~/.bashrc
echo "export HAILO_MODEL_ZOO=~/projects/hailo_model_zoo" >> ~/.bashrc

# Reboot to apply changes
echo "Setup complete. Rebooting in 10 seconds..."
sleep 10
sudo reboot 