# config.py - User configuration for Joy-Con MIDI Controller

# Note: Button codes can be found using evtest or similar tools
# CC numbers should be between 0-127 (standard MIDI range)
# Toggle values are typically 0 (OFF) and 127 (ON)

# Device Configuration
GYRO_MIN = -4100
GYRO_MAX = 4100
JOYSTICK_MIN = -32767
JOYSTICK_MAX = 32767
MIDI_CHANNEL = 0
PRINT_INTERVAL = 0.1
CC_TOGGLE_ON = 127
CC_TOGGLE_OFF = 0

# Control Mappings
GYRO_CC_MAP = {
    'x': 20,  # CC number for X-axis gyro
    'y': 21,  # CC number for Y-axis gyro
    'z': 22   # CC number for Z-axis gyro
}

JOYSTICK_CC_MAP = {
    'x': 23,  # CC number for X-axis joystick
    'y': 24   # CC number for Y-axis joystick
}

# Button Mappings (Button Code: CC Number)
BUTTON_MAPPINGS = {
    # Joy-Con Left button mappings
    309: 60,  # BTN_Z (A button) → CC60
    310: 61,  # BTN_TL → CC61
    311: 62,  # BTN_TR → CC62
    312: 63,  # BTN_TL2 → CC63
    313: 64,  # BTN_TR2 → CC64
    314: 65,  # BTN_SELECT → CC65
    317: 66,  # BTN_THUMBL → CC66
    
    # D-Pad buttons
    544: 67,  # BTN_DPAD_UP → CC67
    545: 68,  # BTN_DPAD_DOWN → CC68
    546: 69,  # BTN_DPAD_LEFT → CC69
    547: 70   # BTN_DPAD_RIGHT → CC70
}

# Optional: Button Names for Display (matches BUTTON_MAPPINGS keys)
BUTTON_NAMES = {
    309: "A",
    310: "L",
    311: "R",
    312: "ZL",
    313: "ZR",
    314: "-",
    317: "THUMB",
    544: "↑",
    545: "↓",
    546: "←",
    547: "→"
}

# MIDI-learn options
MIDILEARN_OPTIONS = {
    1: ('gyro_x', "Gyro X-axis"),
    2: ('gyro_y', "Gyro Y-axis"),
    3: ('gyro_z', "Gyro Z-axis"),
    4: ('joystick_x', "Joystick X-axis"),
    5: ('joystick_y', "Joystick Y-axis"),
    6: ('buttons', "Buttons (all)")
}
