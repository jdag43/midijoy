"""
MIDI handling module

Exposes:
- MIDI scaling functions
- MIDI sending functions
- MIDI-learn functionality
"""

from .mapper import scale_gyro_to_midi, scale_joystick_to_midi
from .sender import send_midi_messages, send_midi_for_learn
from .learner import midi_learn_loop, MidiLearnState, should_send_midi

__all__ = [
    'scale_gyro_to_midi',
    'scale_joystick_to_midi',
    'send_midi_messages',
    'send_midi_for_learn',
    'midi_learn_loop',
    'MidiLearnState',
    'should_send_midi'
]
