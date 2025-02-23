class ContinuousPan:
    def __init__(self, servo, gear_ratio=0.5):
        self.servo = servo
        self.gear_ratio = gear_ratio
        self._current_position = 0  # Degrees
        
    def rotate(self, degrees):
        steps = abs(int(degrees / self.gear_ratio))
        step_size = 1 if degrees > 0 else -1
        for _ in range(steps):
            self._current_position += step_size * self.gear_ratio
            self.servo.angle = (self._current_position % 360) / 180 - 1
            time.sleep(0.01) 