import mido
from mijoco.config.config_loader import ConfigLoader
from mijoco.midi.mapper import scale_gyro_to_midi, scale_joystick_to_midi
from mijoco.devices.detector import JoyConType

config = ConfigLoader()

# Handles all midi output operations
class MidiSender:
    def __init__(self, midi_out):
        self.midi_out = midi_out
        self.channel = config.config['midi']['channel']
    
    def send_cc(self, control, value):
        self.midi_out.send(mido.Message(
            'control_change',
            channel=self.channel,
            control=control,
            value=value
        ))
    
    def send_gyro(self, axis, value):
        """Send gyroscope data as MIDI CC"""
        self.send_cc(config.gyro_cc_map[axis], scale_gyro_to_midi(value))
    
    def send_joystick(self, axis, value, joycon_type: JoyConType):
        """Send joystick data using appropriate mapping"""
        cc_map = (config.joystick_right_cc_map if joycon_type == JoyConType.RIGHT 
                 else config.joystick_left_cc_map)
        self.send_cc(cc_map[axis], scale_joystick_to_midi(value))
    
    def send_button(self, cc, value):
        """Send button state as MIDI CC"""
        self.send_cc(cc, value)

# Send all MIDI messages for normal operation
def send_midi_messages(midi_sender: MidiSender, gyro_values, joycon_values, button_state, gyro_enabled, joystick_enabled, joycon_type: JoyConType):
    # Send gyro data if enabled
    if gyro_enabled:
        for axis in ['x', 'y', 'z']:
            midi_sender.send_gyro(axis, gyro_values[axis])
    # Send joystick data if enabled
    if joystick_enabled:
        for axis in ['x', 'y']:
            midi_sender.send_joystick(axis, joycon_values[axis], joycon_type)
    # Send button data
    for code, pressed in button_state.states.items():
        if pressed:
            midi_sender.send_button(config.button_mappings[code], button_state.cc_values[code])

# Special MIDI sending for learn mode
def send_midi_for_learn(learn_state, midi_sender: MidiSender, gyro_values, joycon_values, button_state, joycon_type: JoyConType):
    control = learn_state.current_selection
    if control == 'gyro_x':
        midi_sender.send_gyro('x', gyro_values['x'])
    elif control == 'gyro_y':
        midi_sender.send_gyro('y', gyro_values['y'])
    elif control == 'gyro_z':
        midi_sender.send_gyro('z', gyro_values['z'])
    elif control in ['joystick_x', 'joystick_rx']:
        midi_sender.send_joystick('x', joycon_values['x'], joycon_type)
    elif control in ['joystick_y', 'joystick_ry']:
        midi_sender.send_joystick('y', joycon_values['y'], joycon_type)
    elif control == 'buttons':
        for code, pressed in button_state.states.items():
            if pressed:
                midi_sender.send_button(config.button_mappings[code], button_state.cc_values[code])