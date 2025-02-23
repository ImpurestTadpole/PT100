import os

class DeploymentConfig:
    PRODUCTION = os.getenv('DEPLOY_ENV', 'development') == 'production'
    MODEL_DIR = os.getenv('MODEL_DIR', '/opt/hailo/models')
    CAMERA_RESOLUTION = os.getenv('CAMERA_RES', '1920x1080')
    WEB_HOST = os.getenv('WEB_HOST', '0.0.0.0')
    WEB_PORT = int(os.getenv('WEB_PORT', 5000))
    SENSOR_POLL_INTERVAL = 0.1 if PRODUCTION else 0.5
    LOG_LEVEL = 'INFO' if PRODUCTION else 'DEBUG'
    
    @classmethod
    def hailo_params(cls):
        return {
            'device_count': 1,
            'scheduling_algorithm': 'NATIVE',
            'batch_size': 4  # Compatible with 4.20.0 SDK
        } 