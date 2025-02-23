def calibrate_servos():
    for angle in range(-90, 91, 10):
        pan_servo.angle = angle
        tilt_servo.angle = angle
        measure_position()
        time.sleep(0.5) 