from gpiozero import AngularServo
from picamera2 import Picamera2

class SafeServo(AngularServo):
    def __init__(self, pin):
        super().__init__(
            pin,
            min_angle=-90,
            max_angle=90,
            min_pulse_width=0.5/1000,
            max_pulse_width=2.5/1000
        )

class Camera:
    def __init__(self):
        self.cam = Picamera2()
        self._configure()
        
    def _configure(self):
        config = self.cam.create_video_configuration()
        self.cam.configure(config)
        
    def start(self):
        self.cam.start()
        
    def get_frame(self):
        return self.cam.capture_array()

class EnhancedServo(AngularServo):
    def __init__(self, pin, **kwargs):
        # Allow full 360 rotation for pan servo
        kwargs.setdefault('min_angle', 0)
        kwargs.setdefault('max_angle', 360)
        super().__init__(pin, **kwargs)
        self._calibration_factor = 1.0
        self._neutral_position = 180  # Center for 360° rotation
        
    def set_gear_ratio(self, ratio):
        self._calibration_factor = ratio
        
    @property
    def calibrated_angle(self):
        return self.angle * self._calibration_factor 

    def optimize_for_rp1(self):
        self.pwm_frequency = 50  # Match RP1's optimal PWM range
        self.pwm_clock = 25e6    # RP1's base clock frequency 

    def set_neutral(self):
        self.angle = self._neutral_position
        
    def calibrate_neutral(self, position):
        self._neutral_position = position 