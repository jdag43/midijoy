from config.config_loader import ConfigLoader

config = ConfigLoader()

def scale_gyro_to_midi(raw_value):
    min_val, max_val = config.gyro_range
    return min(127, max(0, int((raw_value - min_val) * 127 / (max_val - min_val))))

def scale_joystick_to_midi(raw_value):
    min_val, max_val = config.joystick_range
    return min(127, max(0, int((raw_value - min_val) * 127 / (max_val - min_val))))