import evdev
from config import BUTTON_MAPPINGS, CC_TOGGLE_ON, CC_TOGGLE_OFF

class ButtonState:
    def __init__(self):
        self.states = {code: False for code in BUTTON_MAPPINGS.keys()}
        self.cc_values = {code: CC_TOGGLE_OFF for code in BUTTON_MAPPINGS.keys()}

def process_gyro_event(event, gyro_values):
    if event.code == evdev.ecodes.ABS_X:
        gyro_values['x'] = event.value
    elif event.code == evdev.ecodes.ABS_Y:
        gyro_values['y'] = event.value
    elif event.code == evdev.ecodes.ABS_Z:
        gyro_values['z'] = event.value

def process_joystick_event(event, joycon_values):
    if event.code == evdev.ecodes.ABS_X:
        joycon_values['x'] = event.value
    elif event.code == evdev.ecodes.ABS_Y:
        joycon_values['y'] = event.value

def process_button_event(event, button_state):
    if event.code in BUTTON_MAPPINGS and event.type == evdev.ecodes.EV_KEY:
        if event.value == 1:  # Press
            button_state.cc_values[event.code] = \
                CC_TOGGLE_ON if button_state.cc_values[event.code] == CC_TOGGLE_OFF else CC_TOGGLE_OFF
            button_state.states[event.code] = True
        elif event.value == 0:  # Release
            button_state.states[event.code] = False
        return True
    return False

def process_devices(joycon_main, joycon_imu, gyro_values, joycon_values, button_state):
    """Process input from both devices"""
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
                process_joystick_event(event, joycon_values)
            elif event.type == evdev.ecodes.EV_KEY:
                process_button_event(event, button_state)
    except BlockingIOError:
        pass
