class SensorFusion:
    def __init__(self):
        self.imu = ICM20948()
        self._kalman_filter = KalmanFilter()
        
    def get_stabilized_orientation(self):
        accel, gyro, mag = self.imu.read_all()
        return self._kalman_filter.update(accel, gyro, mag) 