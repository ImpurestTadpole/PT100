import cv2
import numpy as np
from hailo_platform import HEF, VDevice
from picamera2 import Picamera2
from gpiozero import AngularServo, DistanceSensor
from icm20948 import ICM20948
import time
import base64
from web_ui import WebInterface
from flask import Response

class PanTiltTracker:
    def __init__(self):
        self.active_model = "yolov5s"
        self.tracking_active = False
        self.models = {
            "yolov5s": "models/yolov5s_face_person.hef",
            "pose_resnet": "models/pose_resnet.hef",
            "efficientdet": "models/efficientdet_lite.hef",
            "nanodet": "models/nanodet.hef"
        }
        self.load_model()

        # Hardware initialization
        self.pan_servo = AngularServo(12, min_angle=-90, max_angle=90)
        self.tilt_servo = AngularServo(13, min_angle=-45, max_angle=45)
        self.ultrasonic = DistanceSensor(echo=24, trigger=23)
        self.imu = ICM20948()
        
        # Camera setup
        self.picam2 = Picamera2()
        self.camera_config = self.picam2.create_video_configuration()
        self.picam2.configure(self.camera_config)
        
        # Tracking parameters
        self.target_class = None
        self.selected_target = None
        self.pan_gear_ratio = 0.5  # 1:2 reduction
        self.pid_params = {'kp': 0.7, 'ki': 0.01, 'kd': 0.05}
        self.integral_x = 0
        self.last_error_x = 0
        self.frame_center = None
        self.pan_servo.set_neutral()
        self.tilt_servo.set_neutral()
        time.sleep(0.5)  # Allow servos to reach neutral

        # Web interface
        self.web_interface = WebInterface(self)
        self.web_interface.start_server()

    def load_model(self):
        if hasattr(self, 'device'):
            self.device.release()
        self.hef = HEF(self.models[self.active_model])
        self.device = VDevice()
        self.network_group = self.device.configure(self.hef)
        self.input_stream, self.output_stream = self.network_group.activate()

    def get_model_classes(self):
        # Get class names from model metadata
        return self.hef.get_model_metadata().classes

    def get_model_metadata(self):
        return {
            "yolov5s": {
                "classes": ["person", "bicycle", "car", ...], # Full COCO classes
                "type": "object_detection"
            },
            "pose_resnet": {
                "classes": ["human_pose"],
                "type": "pose_estimation"
            }
        }

    def preprocess_frame(self, frame):
        # Convert frame for Hailo input
        resized = cv2.resize(frame, (640, 640))
        return np.transpose(resized, (2, 0, 1)).astype(np.float32)

    def calculate_pid(self, error):
        # PID control implementation
        self.integral_x += error
        derivative = error - self.last_error_x
        output = (self.pid_params['kp'] * error +
                 self.pid_params['ki'] * self.integral_x +
                 self.pid_params['kd'] * derivative)
        self.last_error_x = error
        return output

    def update_servos(self, detection):
        if self.frame_center is None:
            return
            
        # Calculate position error
        obj_center = (detection['xmin'] + detection['xmax']) // 2
        error_x = (obj_center - self.frame_center[0]) / self.frame_center[0]
        
        # Apply PID control
        pan_adjustment = self.calculate_pid(error_x)
        self.pan_servo.angle += pan_adjustment * self.pan_gear_ratio
        
        # Add stabilization from IMU
        imu_data = self.imu.read_accelerometer_gyro_data()
        tilt_compensation = imu_data[1] * 0.1  # Adjust based on gyro Y-axis
        self.tilt_servo.angle += tilt_compensation

    def auto_center_target(self):
        # Reset PID controllers
        self.integral_x = 0
        self.last_error_x = 0
        
        # Center servos
        self.pan_servo.set_neutral()
        self.tilt_servo.set_neutral()
        self.frame_center = None  # Reset for next frame

    def run_tracking(self):
        self.picam2.start()
        try:
            while True:
                frame = self.picam2.capture_array()
                # Add bounding boxes to frame
                frame = self.draw_detections(frame)
                # Convert frame to JPEG
                _, jpeg = cv2.imencode('.jpg', frame)
                b64_frame = base64.b64encode(jpeg.tobytes()).decode('utf-8')
                socketio.emit('video_frame', b64_frame)
                
                # Capture and process frame
                self.frame_center = (frame.shape[1]//2, frame.shape[0]//2)
                input_data = self.preprocess_frame(frame)
                
                # Hailo inference
                self.input_stream.send(input_data)
                detections = self.output_stream.recv()
                
                # Process detections
                for det in self.parse_detections(detections):
                    if det['label'] == self.target_class:
                        self.update_servos(det)
                        distance = self.ultrasonic.distance * 100
                        print(f"Tracking {det['label']} at {distance:.1f}cm")
                        break
                
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            self.shutdown()

    def parse_detections(self, raw_output):
        # Implement Hailo-specific output parsing
        # Returns list of detections with {'label': ..., 'xmin': ..., etc.}
        pass

    def draw_detections(self, frame):
        # Add detection visualization logic
        for det in self.parse_detections(detections):
            if det['label'] == self.target_class:
                x1, y1 = det['xmin'], det['ymin']
                x2, y2 = det['xmax'], det['ymax']
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
                cv2.putText(frame, f"{det['label']} {det['confidence']:.2f}",
                           (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
                # Draw trajectory line
                cv2.polylines(frame, [trajectory_points], False, (0,255,0), 2)
                # Add distance text
                cv2.putText(frame, f"{det['distance']:.1f}cm", 
                           (x2+10, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
        return frame

    def shutdown(self):
        self.picam2.stop()
        self.pan_servo.close()
        self.tilt_servo.close()
        self.device.release()

    def generate_raw_frames(self):
        while True:
            frame = self.picam2.capture_array()
            _, jpeg = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

    def generate_processed_frames(self):
        while True:
            frame = self.picam2.capture_array()
            frame = self.draw_detections(frame)
            _, jpeg = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

@app.route('/raw_video_feed')
def raw_video_feed():
    return Response(generate_raw_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/processed_video_feed')
def processed_video_feed():
    return Response(generate_processed_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    tracker = PanTiltTracker()
    tracker.run_tracking() 