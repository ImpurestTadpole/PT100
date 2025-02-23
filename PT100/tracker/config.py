import os

class Config:
    MODEL_DIR = os.getenv('MODEL_DIR', '/opt/hailo/models')
    CAMERA_RES = os.getenv('CAMERA_RES', '1920x1080')
    HAILO_PARAMS = {
        'device_count': 1,
        'scheduling_algorithm': 'HIGH_THROUGHPUT',
        'batch_size': 8,
        'power_mode': 'ULTRA_PERFORMANCE'
    }
    
    @classmethod
    def production(cls):
        return os.getenv('ENV') == 'production'

    PRODUCTION = os.getenv('DEPLOY_ENV', 'development') == 'production'
    WEB_HOST = os.getenv('WEB_HOST', '0.0.0.0')
    WEB_PORT = int(os.getenv('WEB_PORT', 5000))
    SENSOR_POLL_INTERVAL = 0.1 if PRODUCTION else 0.5
    LOG_LEVEL = 'INFO' if PRODUCTION else 'DEBUG' 