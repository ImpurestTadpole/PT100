# Pan-Tilt Object Tracking System
## Overview
This project implements an intelligent pan-tilt tracking system with web-based monitoring and control. Key features include:
- Real-time object detection and tracking using Hailo AI accelerator
- Web interface with live camera view and sensor visualization
- 9-DOF orientation tracking with 3D visualization
- Distance measurement and PID-controlled servo movement
- Automatic target centering and selection

## Hardware Requirements
- Raspberry Pi 4
- Hailo AI Accelerator
- Pan-tilt servo mount
- 2x Servo motors (MG90S or similar)
- Raspberry Pi Camera v2
- ICM20948 IMU sensor
- HC-SR04 Ultrasonic sensor
- GPIO expansion board
- Power supply (5V 3A recommended)

## Software Dependencies
- Python 3.7+
- OpenCV
- NumPy
- Hailo AI Runtime
- picamera2
- Flask
- Flask-SocketIO
- eventlet
- gpiozero
- icm20948-python
- psutil
- matplotlib

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pan-tilt-tracker.git
   cd pan-tilt-tracker
   ```

2. Run the setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. Configure hardware permissions:
   ```bash
   sudo usermod -a -G video,spi,i2c,gpio $USER
   ```

4. Reboot the system after installation completes

## Calibration
1. Servo Calibration:
   ```bash
   python calibrate.py
   ```
   - Follow on-screen instructions to set neutral positions
   - Adjust gear ratios in `tracker/mechanics.py`

2. Camera Alignment:
   ```bash
   python -m tracker.web_ui
   ```
   - Access the web interface at `http://<pi-ip>:5000`
   - Use the calibration tab to align camera FOV

3. PID Tuning:
   - Adjust parameters in `tracker/main.py`:
   ```python
   self.pid_params = {'kp': 0.7, 'ki': 0.01, 'kd': 0.05}  # Default values
   ```

## Usage
1. Start the system:
   ```bash
   python -m tracker.web_ui
   ```

2. Access the web interface:
   ```
   http://<raspberry-pi-ip>:5000
   ```

3. Web interface features:
   - Live camera stream with AI detection overlay
   - Real-time sensor data visualization
   - 3D orientation cube display
   - Target class selection dropdown
   - Manual centering button
   - System health monitoring

4. Control flow:
   ```
   Camera Feed → AI Processing → Target Detection → PID Control → Servo Adjustment
                      ↓              ↓
               Web Interface ← Sensor Data
   ```

## Troubleshooting
Common Issues:
- **Servo Jitter**: Ensure adequate power supply and check PWM settings
- **Camera Not Detected**: Verify ribbon cable connection and enable camera in raspi-config
- **Hailo Detection Failures**: Check model compatibility and Hailo runtime version
- **Web Interface Latency**: Reduce video resolution in `tracker/main.py`

## License
MIT License - See [LICENSE](LICENSE) for details

## Acknowledgments
- Hailo AI for inference acceleration
- Picamera2 library maintainers
- Three.js for 3D visualization
