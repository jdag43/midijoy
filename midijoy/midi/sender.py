import mido
from config import MIDI_CHANNEL, GYRO_CC_MAP, JOYSTICK_CC_MAP, BUTTON_MAPPINGS
from midi.mapper import scale_gyro_to_midi, scale_joystick_to_midi

def send_midi_messages(midi_out, gyro_values, joycon_values, button_state, gyro_enabled, joystick_enabled):
    """Send all MIDI messages for normal operation"""
    if not midi_out:
        return

    if gyro_enabled:
        for axis, cc in GYRO_CC_MAP.items():
            midi_out.send(mido.Message('control_change',
                channel=MIDI_CHANNEL,
                control=cc,
                value=scale_gyro_to_midi(gyro_values[axis])))

    if joystick_enabled:
        for axis, cc in JOYSTICK_CC_MAP.items():
            midi_out.send(mido.Message('control_change',
                channel=MIDI_CHANNEL,
                control=cc,
                value=scale_joystick_to_midi(joycon_values[axis])))

    for code, cc in BUTTON_MAPPINGS.items():
        if button_state.states[code]:
            midi_out.send(mido.Message('control_change',
                channel=MIDI_CHANNEL,
                control=cc,
                value=button_state.cc_values[code]))

def send_midi_for_learn(learn_state, midi_out, gyro_values, joycon_values, button_state):
    """Special MIDI sending for learn mode"""
    if not midi_out:
        return
        
    control = learn_state.current_selection
    if control == 'gyro_x':
        midi_out.send(mido.Message('control_change',
            channel=MIDI_CHANNEL,
            control=GYRO_CC_MAP['x'],
            value=scale_gyro_to_midi(gyro_values['x'])))
    elif control == 'gyro_y':
        midi_out.send(mido.Message('control_change',
            channel=MIDI_CHANNEL,
            control=GYRO_CC_MAP['y'],
            value=scale_gyro_to_midi(gyro_values['y'])))
    elif control == 'gyro_z':
        midi_out.send(mido.Message('control_change',
            channel=MIDI_CHANNEL,
            control=GYRO_CC_MAP['z'],
            value=scale_gyro_to_midi(gyro_values['z'])))
    elif control == 'joystick_x':
        midi_out.send(mido.Message('control_change',
            channel=MIDI_CHANNEL,
            control=JOYSTICK_CC_MAP['x'],
            value=scale_joystick_to_midi(joycon_values['x'])))
    elif control == 'joystick_y':
        midi_out.send(mido.Message('control_change',
            channel=MIDI_CHANNEL,
            control=JOYSTICK_CC_MAP['y'],
            value=scale_joystick_to_midi(joycon_values['y'])))
    elif control == 'buttons':
        for code, pressed in button_state.states.items():
            if pressed:
                midi_out.send(mido.Message('control_change',
                    channel=MIDI_CHANNEL,
                    control=BUTTON_MAPPINGS[code],
                    value=button_state.cc_values[code]))
