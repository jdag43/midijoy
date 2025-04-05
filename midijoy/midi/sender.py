import mido
from config.config_loader import ConfigLoader
from midi.mapper import scale_gyro_to_midi, scale_joystick_to_midi

config = ConfigLoader()

def send_midi_messages(midi_out, gyro_values, joycon_values, button_state, gyro_enabled, joystick_enabled):
    """Send all MIDI messages for normal operation"""
    if not midi_out:
        return

    midi_channel = config.config['midi']['channel']

    # Send gyro data if enabled
    if gyro_enabled:
        for axis, cc in config.gyro_cc_map.items():
            midi_out.send(mido.Message(
                'control_change',
                channel=midi_channel,
                control=cc,
                value=scale_gyro_to_midi(gyro_values[axis])
                )
            )

    # Send joystick data if enabled
    if joystick_enabled:
        for axis, cc in config.joystick_cc_map.items():
            midi_out.send(mido.Message(
                'control_change',
                channel=midi_channel,
                control=cc,
                value=scale_joystick_to_midi(joycon_values[axis])
                )
            )

    # Send button data
    for code, cc in config.button_mappings.items():
        if button_state.states[code]:
            midi_out.send(mido.Message(
                'control_change',
                channel=midi_channel,
                control=cc,
                value=button_state.cc_values[code]
                )
            )

def send_midi_for_learn(learn_state, midi_out, gyro_values, joycon_values, button_state):
    """Special MIDI sending for learn mode"""
    if not midi_out:
        return
        
    midi_channel = config.config['midi']['channel']
    control = learn_state.current_selection

    if control == 'gyro_x':
        midi_out.send(mido.Message(
            'control_change',
            channel=midi_channel,
            control=config.gyro_cc_map['x'],
            value=scale_gyro_to_midi(gyro_values['x']))
        )
    elif control == 'gyro_y':
        midi_out.send(mido.Message(
            'control_change',
            channel=midi_channel,
            control=config.gyro_cc_map['y'],
            value=scale_gyro_to_midi(gyro_values['y']))
        )
    elif control == 'gyro_z':
        midi_out.send(mido.Message(
            'control_change',
            channel=midi_channel,
            control=config.gyro_cc_map['z'],
            value=scale_gyro_to_midi(gyro_values['z']))
        )
    elif control == 'joystick_x':
        midi_out.send(mido.Message(
            'control_change',
            channel=midi_channel,
            control=config.joystick_cc_map['x'],
            value=scale_joystick_to_midi(joycon_values['x']))
        )
    elif control == 'joystick_y':
        midi_out.send(mido.Message(
            'control_change',
            channel=midi_channel,
            control=config.joystick_cc_map['y'],
            value=scale_joystick_to_midi(joycon_values['y']))
        )
    elif control == 'buttons':
        for code, pressed in button_state.states.items():
            if pressed:
                midi_out.send(mido.Message(
                    'control_change',
                    channel=midi_channel,
                    control=config.button_mappings[code],
                    value=button_state.cc_values[code])
                )