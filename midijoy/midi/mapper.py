from config import GYRO_MIN, GYRO_MAX, JOYSTICK_MIN, JOYSTICK_MAX

def scale_gyro_to_midi(raw_value):
    return min(127, max(0, int((raw_value - GYRO_MIN) * 127 / (GYRO_MAX - GYRO_MIN))))

def scale_joystick_to_midi(raw_value):
    return min(127, max(0, int((raw_value - JOYSTICK_MIN) * 127 / (JOYSTICK_MAX - JOYSTICK_MIN))))
