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