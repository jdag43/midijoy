import time
import sys
import argparse
import evdev
from config.config_loader import ConfigLoader
from devices.detector import find_joycon, select_midi_output
from devices.handler import ButtonState, process_gyro_event, process_joystick_event, process_button_event
from midi.mapper import scale_gyro_to_midi, scale_joystick_to_midi
from midi.sender import send_midi_messages
from midi.learner import midi_learn_loop

# Initialize configuration
config = ConfigLoader()
def print_values(gyro_values, joycon_values, gyro_enabled, joystick_enabled, button_state):
    gyro_status = "ON " if gyro_enabled else "OFF"
    joystick_status = "ON " if joystick_enabled else "OFF"

    active_buttons = []
    toggle_on = config.config['midi'].get('toggle', {}).get('on', 127)  # Get toggle ON value
    toggle_off = config.config['midi'].get('toggle', {}).get('off', 0)  # Get toggle OFF value
    
    for code in config.button_mappings.keys():
        if button_state.states.get(code, False):
            state = "ON" if button_state.cc_values[code] == toggle_on else "OFF"
            active_buttons.append(f"{config.button_names.get(code, '?')}({state})")

    output = (
        f"\rGyro: X:{gyro_values['x']:6d} | Y:{gyro_values['y']:6d} | Z:{gyro_values['z']:6d} "
        f"[MIDI:{gyro_status}] | "
        f"Joy: X:{joycon_values['x']:6d} | Y:{joycon_values['y']:6d} | "
        f"Buttons: {','.join(active_buttons) if active_buttons else 'None'}"
    )
    sys.stdout.write(output)
    sys.stdout.flush()

def print_configuration(midi_out, gyro_enabled, joystick_enabled):
    if not midi_out:
        print("\nRunning in preview mode (no MIDI output)")
    else:
        print("\nActive MIDI Configuration:")
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
            for axis, cc in config.joystick_cc_map.items():
                print(f"  {axis.upper()}-axis → CC{cc}")
        
        print("\nButtons:")
        for code, cc in config.button_mappings.items():
            print(f"  {config.button_names.get(code, 'Unknown')} → CC{cc} (Toggle ON/OFF)")

def main_loop(joycon_main, joycon_imu, midi_out, gyro_enabled, joystick_enabled):
    gyro_values = {'x': 0, 'y': 0, 'z': 0}
    joycon_values = {'x': 0, 'y': 0}
    button_state = ButtonState()
    last_print = 0

    try:
        while True:
            current_time = time.time()
            new_data = False

            try:
                for event in joycon_imu.read():
                    if event.type == evdev.ecodes.EV_ABS:
                        process_gyro_event(event, gyro_values)
                        new_data = True
            except BlockingIOError:
                pass

            try:
                for event in joycon_main.read():
                    if event.type == evdev.ecodes.EV_ABS:
                        process_joystick_event(event, joycon_values)
                        new_data = True
                    elif event.type == evdev.ecodes.EV_KEY:
                        if process_button_event(event, button_state):
                            new_data = True
            except BlockingIOError:
                pass

            if new_data and midi_out:
                send_midi_messages(midi_out, gyro_values, joycon_values, button_state, gyro_enabled, joystick_enabled)

            if current_time - last_print >= config.config.get('print_interval', 0.1):
                print_values(gyro_values, joycon_values, gyro_enabled, joystick_enabled, button_state)
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
    joycon_main, joycon_imu = find_joycon()
    if not joycon_main or not joycon_imu:
        return

    midi_out = select_midi_output()
    
    gyro_enabled = not args.no_gyro
    joystick_enabled = not args.no_joystick
    
    if args.midi_learn:
        if not midi_out:
            print("Error: MIDI output required for MIDI Learn mode")
            return
            
        learned_mappings = midi_learn_loop(joycon_main, joycon_imu, midi_out)
        gyro_enabled = learned_mappings['gyro_x'] or learned_mappings['gyro_y'] or learned_mappings['gyro_z']
        joystick_enabled = learned_mappings['joystick_x'] or learned_mappings['joystick_y']
    
    print_configuration(midi_out, gyro_enabled, joystick_enabled)
    print("\nStarting main loop... (Ctrl+C to exit)\n")

    try:
        main_loop(joycon_main, joycon_imu, midi_out, gyro_enabled, joystick_enabled)
    finally:
        joycon_main.close()
        joycon_imu.close()
        if midi_out:
            midi_out.close()

if __name__ == "__main__":
    main()
