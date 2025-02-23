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

# Install base requirements
pip3 install -r requirements/base.txt

# Install Hailo dependencies
pip3 install -r requirements/hailo.txt

# Install web interface dependencies
pip3 install -r requirements/web.txt

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

# Configure HAT power
echo "dtoverlay=gpio-poweroff,gpiopin=4,active_low=1" | sudo tee -a /boot/firmware/config.txt
sudo apt install -y hailo-hat-powerctl

# Auto-detect hardware and install appropriate drivers
if grep -q "Raspberry Pi 5" /proc/device-tree/model; then
    echo "Installing Pi 5 specific dependencies..."
    sudo apt install -y raspberrypi-kernel-headers hailo-rpi5-driver
    # Optimize filesystems for SSD users
    sudo tune2fs -O dir_index,has_journal,extent /dev/mmcblk0p2
fi

# Add log rotation
sudo tee /etc/logrotate.d/pan_tilt <<EOL
/var/log/pan_tilt.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 640 root adm
}
EOL

# Add systemd service
sudo tee /etc/systemd/system/pan-tilt.service <<EOL
[Unit]
Description=Pan-Tilt Tracking System
After=network.target

[Service]
User=pi
ExecStart=/usr/bin/python3 -m tracker.web_ui --production
WorkingDirectory=/home/pi/pan_tilt_tracker
Environment=PYTHONUNBUFFERED=1
Environment=HAILO_DEPLOYMENT_MODE=production
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

# Reboot to apply changes
echo "Setup complete. Rebooting in 10 seconds..."
sleep 10
sudo reboot 