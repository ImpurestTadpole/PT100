# Pan-Tilt Object Tracking System
## Overview
Advanced AI-powered tracking system optimized for Raspberry Pi 5. Features real-time object detection, servo control, and sensor integration with web-based monitoring.

![System Diagram](system-diagram.png)

## Hardware Setup (Pi 5 Specific)
### Required Components
| Component          | Specification                  |
|--------------------|--------------------------------|
| Raspberry Pi       | 5 (8GB recommended)           |
| Hailo AI Accelerator| Hailo-8L                       |
| Camera Module      | Official Pi Camera Module 3    |
| Servo Motors       | MG90S (360° continuous rotation) |
| IMU                | ICM20948 9-DOF                |
| Ultrasonic Sensor  | HC-SR04                       |

### GPIO Pin Configuration
| Component          | Pi 5 GPIO Pin | Notes                          |
|--------------------|---------------|--------------------------------|
| Pan Servo          | GPIO12        | PWM0 channel                  |
| Tilt Servo         | GPIO13        | PWM1 channel                  |
| Ultrasonic Trigger | GPIO23        |                               |
| Ultrasonic Echo    | GPIO24        |                               |
| I2C SDA (IMU)      | GPIO0         | ID_SD                         |
| I2C SCL (IMU)      | GPIO1         | ID_SC                         |
| Hailo Accelerator  | USB-C         | Use Pi 5's USB-C port         |

## Installation (Pi 5 Specific)
1. **Flash Raspberry Pi OS**  
   Use 64-bit Bookworm release (2024-01-01 or newer)

2. **System Configuration**
   ```bash
   sudo raspi-config nonint do_i2c 0
   sudo raspi-config nonint do_legacy 0
   sudo raspi-config nonint do_memory_split 256
   sudo raspi-config nonint do_camera 1
   ```

3. **Install Dependencies**
   ```bash
   sudo apt update && sudo apt full-upgrade -y
   sudo apt install -y python3.11 python3-pip libopenblas-dev libhailort5
   ```

4. **Hailo Setup**
   ```bash
   wget https://hailo.ai/pi5/hailort_5.1.0_arm64.deb
   sudo dpkg -i hailort_5.1.0_arm64.deb
   sudo usermod -aG video,hailort $USER
   ```

5. **Project Setup**
   ```bash
   git clone https://github.com/yourusername/pan-tilt-tracker.git
   cd pan-tilt-tracker
   ./setup.sh
   ```

## Calibration Procedure
1. **Servo Alignment**
   ```bash
   python calibrate.py --pan-pin 12 --tilt-pin 13
   ```
   - Follow on-screen instructions to set neutral positions
   - Adjust gear ratios in `tracker/mechanics.py`

2. **IMU Calibration**
   ```bash
   python -m tracker.sensors --calibrate
   ```
   - Keep device stable during 10-second calibration

3. **Camera Alignment**
   ```bash
   python -m tracker.web_ui --calibrate
   ```
   - Use web interface grid overlay for alignment

## Usage
**Starting the System**
```bash
python -m tracker.web_ui --model yolov5s --resolution 1920x1080
```

**Web Interface Features**
- Live dual camera view (raw + AI overlay)
- Real-time servo position control (0-360° pan, 0-180° tilt)
- Sensor fusion visualization (3D orientation cube)
- Model selection (Object Detection/Pose Estimation)
- System health monitoring (CPU/GPU/Mem)

**Access Interface**
```
http://<pi5-ip>:5000
```

## Pi 5 Specific Notes
1. **Power Requirements**
   - Use official 27W USB-C PD supply
   - Add 1000µF capacitor across servo power lines

2. **RP1 Controller**
   ```python
   # In mechanics.py
   servo.optimize_for_rp1()  # Enable Pi 5's RP1 PWM optimizations
   ```

3. **Troubleshooting**
   - **Servo Jitter**: Update to latest firmware `sudo rpi-eeprom-update`
   - **Camera Issues**: Check `/dev/video0` exists
   - **Hailo Detection**: Verify USB-C connection status `hailortcli scan`

## License
MIT License - See [LICENSE](LICENSE) for details

## Acknowledgments
- Hailo AI for Pi 5 optimized models
- Raspberry Pi Ltd for RP1 documentation
- Picamera2 maintainers for Pi 5 support
