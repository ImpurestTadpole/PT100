from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import json
import time
from three import Scene, PerspectiveCamera, WebGLRenderer, BoxGeometry, MeshBasicMaterial, Mesh
import psutil
from config import DeploymentConfig

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')

class WebInterface:
    def __init__(self, tracker):
        self.tracker = tracker
        self.running = False
        self.thread = None

    def start_server(self):
        self.running = True
        self.thread = threading.Thread(target=self._run_server)
        self.thread.start()

    def _run_server(self):
        if DeploymentConfig.PRODUCTION:
            from gevent import monkey
            monkey.patch_all()
            socketio.run(app, 
                        host=DeploymentConfig.WEB_HOST,
                        port=DeploymentConfig.WEB_PORT,
                        log_output=DeploymentConfig.PRODUCTION,
                        use_reloader=False,
                        debug=False)
        else:
            socketio.run(app, 
                        host=DeploymentConfig.WEB_HOST,
                        port=DeploymentConfig.WEB_PORT,
                        debug=True)

    def send_sensor_data(self):
        while self.running:
            sensor_data = {
                'distance': self.tracker.ultrasonic.distance * 100,
                'orientation': self.tracker.imu.read_accelerometer_gyro_data(),
                'pan_angle': self.tracker.pan_servo.angle,
                'tilt_angle': self.tracker.tilt_servo.angle
            }
            socketio.emit('sensor_update', json.dumps(sensor_data))
            time.sleep(0.1)

    def create_3d_visualization(self):
        self.scene = Scene()
        self.camera = PerspectiveCamera(75, 1, 0.1, 1000)
        self.renderer = WebGLRenderer()
        self.cube = Mesh(
            BoxGeometry(1, 1, 1),
            MeshBasicMaterial({ 'color': 0x00ff00, 'wireframe': True })
        )
        self.scene.add(self.cube)
        self.camera.position.z = 2

    def update_3d_visualization(self, orientation):
        self.cube.rotation.x = orientation[0]
        self.cube.rotation.y = orientation[1]
        self.cube.rotation.z = orientation[2]
        self.renderer.render(self.scene, self.camera)

    def get_system_stats(self):
        return {
            'cpu': psutil.cpu_percent(),
            'memory': psutil.virtual_memory().percent,
            'temperature': self.read_cpu_temp(),
            'fps': self.calculate_fps()
        }

    def send_system_stats(self):
        while self.running:
            stats = self.get_system_stats()
            socketio.emit('system_stats', stats)
            time.sleep(2)

@app.route('/')
def index():
    return render_template('interface.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('select_target')
def handle_target_selection(data):
    tracker.target_class = data['class']
    tracker.auto_center_target()
    print(f"New target selected: {data['class']}")

@socketio.on('center_camera')
def handle_center_command():
    tracker.auto_center_target()
    print("Camera centering commanded")

@socketio.on('select_model')
def handle_model_selection(data):
    tracker.active_model = data['model']
    tracker.load_model()
    classes = tracker.get_model_classes()
    socketio.emit('model_classes', {'classes': classes})
    print(f"Loaded model: {data['model']}")

@socketio.on('toggle_tracking')
def handle_tracking_toggle(data):
    tracker.tracking_active = data['state']
    print(f"Tracking {'active' if data['state'] else 'paused'}")

@socketio.on('set_servo')
def handle_servo_control(data):
    if data['type'] == 'pan':
        tracker.pan_servo.angle = float(data['angle'])
    elif data['type'] == 'tilt':
        tracker.tilt_servo.angle = float(data['angle'])
    print(f"Set {data['type']} to {data['angle']}°")

if __name__ == '__main__':
    tracker = PanTiltTracker(target_class="person")
    web_interface = WebInterface(tracker)
    web_interface.start_server()
    tracker.run_tracking() 