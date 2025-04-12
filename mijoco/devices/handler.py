import evdev
from mijoco.config.config_loader import ConfigLoader
from .detector import JoyConType

config = ConfigLoader()

# Axis codes
ABS_X = 0
ABS_Y = 1
ABS_RX = 3
ABS_RY = 4

class ButtonState:
    def __init__(self):
        self.states = {code: False for code in config.button_mappings.keys()}
        
        # Get toggle values with defaults in case they're not in config
        toggle_config = config.config.get('midi', {}).get('toggle', {})
        toggle_off = toggle_config.get('off', 0)  # Default to 0 if not specified
        toggle_on = toggle_config.get('on', 127)  # Default to 127 if not specified
        
        self.cc_values = {code: toggle_off for code in config.button_mappings.keys()}
        self.toggle_on = toggle_on
        self.toggle_off = toggle_off

def process_gyro_event(event, gyro_values):
    if event.code == evdev.ecodes.ABS_X:
        gyro_values['x'] = event.value
    elif event.code == evdev.ecodes.ABS_Y:
        gyro_values['y'] = event.value
    elif event.code == evdev.ecodes.ABS_Z:
        gyro_values['z'] = event.value

def process_joystick_event(event, joycon_values, joycon_type: JoyConType):
    if joycon_type == JoyConType.RIGHT:
        if event.code == 3:  # ABS_RX
            joycon_values['x'] = event.value
        elif event.code == 4:  # ABS_RY
            joycon_values['y'] = event.value
    else:
        if event.code == 0:  # ABS_X
            joycon_values['x'] = event.value
        elif event.code == 1:  # ABS_Y
            joycon_values['y'] = event.value

def process_button_event(event, button_state):
    if event.code in config.button_mappings and event.type == evdev.ecodes.EV_KEY:
        if event.value == 1:  # Press
            button_state.cc_values[event.code] = \
                button_state.toggle_on if button_state.cc_values[event.code] == button_state.toggle_off else button_state.toggle_off
            button_state.states[event.code] = True
        elif event.value == 0:  # Release
            button_state.states[event.code] = False
        return True
    return False

# Process input from IMU and main devices
def process_devices(joycon_main, joycon_imu, gyro_values, joycon_values, button_state, joycon_type: JoyConType):
    # Process IMU device events
    try:
        for event in joycon_imu.read():
            if event.type == evdev.ecodes.EV_ABS:
                process_gyro_event(event, gyro_values)
    except BlockingIOError:
        pass
    # Process main device events
    try:
        for event in joycon_main.read():
            if event.type == evdev.ecodes.EV_ABS:
                process_joystick_event(event, joycon_values, joycon_type)
            elif event.type == evdev.ecodes.EV_KEY:
                process_button_event(event, button_state)
    except BlockingIOError:
        pass
