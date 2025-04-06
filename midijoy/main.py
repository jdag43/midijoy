import time
import sys
import argparse
import evdev
from config.config_loader import ConfigLoader
from devices.detector import find_joycon, select_midi_output
from devices.handler import ButtonState, process_devices, process_gyro_event, process_joystick_event, process_button_event
from midi.mapper import scale_gyro_to_midi, scale_joystick_to_midi
from midi.sender import MidiSender, send_midi_messages
from midi.learner import midi_learn_loop
from devices.detector import JoyConType

# Initialize configuration
config = ConfigLoader()

def print_values(gyro_values, joycon_values, gyro_enabled, joystick_enabled, button_state, joycon_type: JoyConType):
    gyro_status = "ON " if gyro_enabled else "OFF"
    joystick_status = "ON " if joystick_enabled else "OFF"

    active_buttons = []
    toggle_on = config.config['midi'].get('toggle', {}).get('on', 127)
    toggle_off = config.config['midi'].get('toggle', {}).get('off', 0)
    
    for code in config.button_mappings.keys():
        if button_state.states.get(code, False):
            state = "ON" if button_state.cc_values[code] == toggle_on else "OFF"
            active_buttons.append(f"{config.button_names.get(code, '?')}({state})")

    output = (
        f"\r[{joycon_type.value}] Gyro: X:{gyro_values['x']:6d} | Y:{gyro_values['y']:6d} | Z:{gyro_values['z']:6d} "
        f"[MIDI:{gyro_status}] | "
        f"Joy: X:{joycon_values['x']:6d} | Y:{joycon_values['y']:6d} | "
        f"Buttons: {','.join(active_buttons) if active_buttons else 'None'}"
    )
    sys.stdout.write(output)
    sys.stdout.flush()

def print_configuration(midi_out, gyro_enabled, joystick_enabled, joycon_type: JoyConType):
    if not midi_out:
        print("\nRunning in preview mode (no MIDI output)")
    else:
        print("\nActive MIDI Configuration:")
        print(f"Using Joy-Con: {joycon_type.value}")
        print(f"MIDI Channel: {config.config['midi']['channel']}")
        print(f"Gyro Output: {'Enabled' if gyro_enabled else 'Disabled'}")
        print(f"Joystick Output: {'Enabled' if joystick_enabled else 'Disabled'}")
        
        print("\nControl Assignments:")
        if gyro_enabled:
            print("Gyro:")
            for axis, cc in config.gyro_cc_map.items():
                print(f"  {axis.upper()}-axis → CC{cc}")
        
        if joystick_enabled:
            print("\nJoystick:")
            joystick_map = (config.joystick_right_cc_map if joycon_type == JoyConType.RIGHT 
                          else config.joystick_left_cc_map)
            for axis, cc in joystick_map.items():
                print(f"  {axis.upper()}-axis → CC{cc}")
        
        print("\nButtons:")
        for code, cc in config.button_mappings.items():
            name = config.button_names.get(code, 'Unknown')
            if joycon_type.value in name or '(' not in name:
                print(f"  {name.split('(')[0].strip()} → CC{cc}")

def main_loop(joycon_main, joycon_imu, midi_out, gyro_enabled, joystick_enabled, joycon_type: JoyConType):
    gyro_values = {'x': 0, 'y': 0, 'z': 0}
    joycon_values = {'x': 0, 'y': 0}
    button_state = ButtonState()
    midi_sender = MidiSender(midi_out)
    last_print = 0

    try:
        while True:
            current_time = time.time()
            new_data = False
            
            # Unified device processing
            try:
                process_devices(joycon_main, joycon_imu, gyro_values, joycon_values, 
                              button_state, joycon_type)
                new_data = any([
                    joycon_values['x'] != 0,
                    joycon_values['y'] != 0,
                    any(button_state.states.values()),
                    gyro_values['x'] != 0,
                    gyro_values['y'] != 0,
                    gyro_values['z'] != 0
                ])
            except BlockingIOError:
                pass

            if new_data and midi_out:
                send_midi_messages(midi_sender, gyro_values, joycon_values,
                                 button_state, gyro_enabled, joystick_enabled,
                                 joycon_type)

            if current_time - last_print >= config.config.get('print_interval', 0.1):
                print_values(gyro_values, joycon_values, gyro_enabled,
                           joystick_enabled, button_state, joycon_type)
                last_print = current_time

            time.sleep(0.001)

    except KeyboardInterrupt:
        print("\nExiting...")

def main():
    parser = argparse.ArgumentParser(description="Joy-Con MIDI Controller")
    parser.add_argument("--no-gyro", action="store_true", help="Disable Gyroscope MIDI output")
    parser.add_argument("--no-joystick", action="store_true", help="Disable Joystick MIDI output")
    parser.add_argument("--midi-learn", action="store_true", help="Enable MIDI learn mode")
    args = parser.parse_args()

    print("Starting Joy-Con MIDI controller...")
    joycon_main, joycon_imu, joycon_type = find_joycon()
    if not joycon_main or not joycon_imu:
        return

    midi_out = select_midi_output()
    midi_sender = MidiSender(midi_out)
    gyro_enabled = not args.no_gyro
    joystick_enabled = not args.no_joystick
    
    if args.midi_learn:
        learned_mappings = midi_learn_loop(joycon_main, joycon_imu, midi_out, joycon_type)
        gyro_enabled = learned_mappings['gyro_x'] or learned_mappings['gyro_y'] or learned_mappings['gyro_z']
        joystick_enabled = learned_mappings['joystick_x'] or learned_mappings['joystick_y'] or learned_mappings['joystick_rx'] or learned_mappings['joystick_ry']
    
    print_configuration(midi_out, gyro_enabled, joystick_enabled, joycon_type)
    print("\nStarting main loop... (Ctrl+C to exit)\n")

    try:
        main_loop(joycon_main, joycon_imu, midi_out, gyro_enabled, joystick_enabled, joycon_type)
    finally:
        joycon_main.close()
        joycon_imu.close()
        if midi_out:
            midi_out.close()

if __name__ == "__main__":
    main()