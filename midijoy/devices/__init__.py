"""
Joy-Con device handling module

Exposes:
- ButtonState class
- Device detection functions
- Input processing functions
"""

from .detector import find_joycon, select_midi_output
from .handler import (
    ButtonState,
    process_gyro_event,
    process_joystick_event,
    process_button_event,
    process_devices
)

__all__ = [
    'find_joycon',
    'select_midi_output',
    'ButtonState',
    'process_gyro_event',
    'process_joystick_event',
    'process_button_event',
    'process_devices'
]
