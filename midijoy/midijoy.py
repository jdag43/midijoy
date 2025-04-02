import evdev
import mido
import argparse
import sys
import time
import select

from config import (
    GYRO_MIN, GYRO_MAX,
    JOYSTICK_MIN, JOYSTICK_MAX,
    MIDI_CHANNEL, PRINT_INTERVAL,
    CC_TOGGLE_ON, CC_TOGGLE_OFF,
    GYRO_CC_MAP, JOYSTICK_CC_MAP,
    BUTTON_MAPPINGS, BUTTON_NAMES
)

class ButtonState:
    def __init__(self):
        self.states = {code: False for code in BUTTON_MAPPINGS.keys()}
        self.cc_values = {code: CC_TOGGLE_OFF for code in BUTTON_MAPPINGS.keys()}

def scale_gyro_to_midi(raw_value):
    """Scale gyro values (GYRO_MIN to GYRO_MAX) → MIDI (0-127)"""
    return min(127, max(0, int((raw_value - GYRO_MIN) * 127 / (GYRO_MAX - GYRO_MIN))))

def scale_joystick_to_midi(raw_value):
    """Scale joystick values (-32767 to 32767) → MIDI (0-127)"""
    return min(127, max(0, int((raw_value - JOYSTICK_MIN) * 127 / (JOYSTICK_MAX - JOYSTICK_MIN))))


def find_joycon():
    """Find both Joy-Con devices with verbose logging"""
    print("\nSearching for Joy-Con devices...")
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    
    joycon_main = joycon_imu = None
    for device in devices:
        if "Joy-Con (L) (IMU)" in device.name:
            joycon_imu = device
            print(f"Found IMU device: {device.name} at {device.path}")
        elif "Joy-Con (L)" in device.name and "(IMU)" not in device.name:
            joycon_main = device
            print(f"Found main device: {device.name} at {device.path}")

    if not joycon_main or not joycon_imu:
        print("\nError: Could not find required Joy-Con devices!")
        if not joycon_main:
            print("- Main Joy-Con device missing")
        if not joycon_imu:
            print("- IMU Joy-Con device missing")
        print("Available devices:")
        for i, device in enumerate(devices):
            print(f"  {i}: {device.path} - {device.name}")
    else:
        print("\nJoy-Con devices successfully detected!")

    return joycon_main, joycon_imu


def select_midi_output():
    """Let user select MIDI output from available devices"""
    outputs = mido.get_output_names()
    if not outputs:
        print("No MIDI output devices found!")
        return None

    print("\nAvailable MIDI outputs:")
    for i, name in enumerate(outputs):
        print(f"{i}: {name}")

    while True:
        try:
            selection = input("Enter device number (or 'q' to skip): ")
            if selection.lower() == 'q':
                print("Continuing without MIDI output (preview mode)")
                return None
            index = int(selection)
            if 0 <= index < len(outputs):
                device = mido.open_output(outputs[index])
                print(f"Connected to MIDI output: {device.name}")
                return device
            print("Invalid selection. Try again.")
        except ValueError:
            print("Please enter a number or 'q' to quit.")


def print_configuration(midi_out, gyro_enabled, joystick_enabled):
    """Print the current configuration"""
    if not midi_out:
        print("\nRunning in preview mode (no MIDI output)")
    else:
        print("\nActive MIDI Configuration:")
        print(f"MIDI Channel: {MIDI_CHANNEL}")
        print(f"Gyro Output: {'Enabled' if gyro_enabled else 'Disabled'}")
        print(f"Joystick Output: {'Enabled' if joystick_enabled else 'Disabled'}")
        
        print("\nControl Assignments:")
        if gyro_enabled:
            print("Gyro:")
            for axis, cc in GYRO_CC_MAP.items():
                print(f"  {axis.upper()}-axis → CC{cc}")
        
        if joystick_enabled:
            print("\nJoystick:")
            for axis, cc in JOYSTICK_CC_MAP.items():
                print(f"  {axis.upper()}-axis → CC{cc}")
        
        print("\nButtons:")
        for code, cc in BUTTON_MAPPINGS.items():
            print(f"  {BUTTON_NAMES.get(code, 'Unknown')} → CC{cc} (Toggle ON/OFF)")

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
    """Handle button toggle events"""
    if event.code in BUTTON_MAPPINGS and event.type == evdev.ecodes.EV_KEY:
        if event.value == 1:  # Only on press
            # Toggle the value
            button_state.cc_values[event.code] = \
                CC_TOGGLE_ON if button_state.cc_values[event.code] == CC_TOGGLE_OFF else CC_TOGGLE_OFF
            button_state.states[event.code] = True
        elif event.value == 0:  # On release
            button_state.states[event.code] = False
        return True
    return False

def print_values(gyro_values, joycon_values, gyro_enabled, joystick_enabled, button_state):
    gyro_status = "ON " if gyro_enabled else "OFF"
    joystick_status = "ON " if joystick_enabled else "OFF"
    
    # Get active buttons and their states
    active_buttons = []
    for code in BUTTON_MAPPINGS.keys():
        if button_state.states.get(code, False):
            state = "ON" if button_state.cc_values[code] == CC_TOGGLE_ON else "OFF"
            active_buttons.append(f"{BUTTON_NAMES.get(code, '?')}({state})")
    output = (
        f"\rGyro: X:{gyro_values['x']:6d} | Y:{gyro_values['y']:6d} | Z:{gyro_values['z']:6d} "
        f"[MIDI:{gyro_status}] | "
        f"Joy: X:{joycon_values['x']:6d} | Y:{joycon_values['y']:6d} | "
        f"Buttons: {','.join(active_buttons) if active_buttons else 'None'}"
    )
    sys.stdout.write(output)
    sys.stdout.flush()

def send_midi_messages(midi_out, gyro_values, joycon_values, button_state, gyro_enabled, joystick_enabled):
    """Send all MIDI messages"""
    if not midi_out:
        return
    
    # Continuous gyro messages (if enabled)
    if gyro_enabled:
        for axis, cc in GYRO_CC_MAP.items():
            midi_out.send(mido.Message('control_change',
                channel=MIDI_CHANNEL,
                control=cc,
                value=scale_gyro_to_midi(gyro_values[axis])))
    
    # Continuous joystick messages (if enabled)
    if joystick_enabled:
        for axis, cc in JOYSTICK_CC_MAP.items():
            midi_out.send(mido.Message('control_change',
                channel=MIDI_CHANNEL,
                control=cc,
                value=scale_joystick_to_midi(joycon_values[axis])))
    
    # Button toggle messages
    for code, cc in BUTTON_MAPPINGS.items():
        if button_state.states[code]:  # Only if button is active
            midi_out.send(mido.Message('control_change',
                channel=MIDI_CHANNEL,
                control=cc,
                value=button_state.cc_values[code]))

def main_loop(joycon_main, joycon_imu, midi_out, gyro_enabled, joystick_enabled):
    gyro_values = {'x': 0, 'y': 0, 'z': 0}
    joycon_values = {'x': 0, 'y': 0}
    button_state = ButtonState()
    last_print = 0
    
    try:
        while True:
            current_time = time.time()
            new_data = False
            
            # Process IMU device events
            try:
                for event in joycon_imu.read():
                    if event.type == evdev.ecodes.EV_ABS:
                        process_gyro_event(event, gyro_values)
                        new_data = True
            except BlockingIOError:
                pass
            
            # Process main device events
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
            
            # Send MIDI if we have new data
            if new_data and midi_out:
                send_midi_messages(midi_out, gyro_values, joycon_values, button_state, gyro_enabled, joystick_enabled)
            
            # Print at fixed interval
            if current_time - last_print >= PRINT_INTERVAL:
                print_values(gyro_values, joycon_values, gyro_enabled, joystick_enabled, button_state)
                last_print = current_time
            
            time.sleep(0.001)
            
    except KeyboardInterrupt:
        print("\nExiting...")



class MidiLearnState:
    def __init__(self):
        self.active = False
        self.current_selection = None
        self.learned_mappings = {
            'gyro_x': False,
            'gyro_y': False,
            'gyro_z': False,
            'joystick_x': False,
            'joystick_y': False,
            'buttons': False
        }

def print_midilearn_menu():
    print("\nMIDI Learn Menu:")
    print("1: Gyro X-axis")
    print("2: Gyro Y-axis")
    print("3: Gyro Z-axis")
    print("4: Joystick X-axis")
    print("5: Joystick Y-axis")
    print("6: Buttons (all)")
    print("q: Finish MIDI Learn and start normal operation")
    print("\nSelect a control to learn (1-6) or 'q' to finish:")

def midi_learn_loop(joycon_main, joycon_imu, midi_out):
    learn_state = MidiLearnState()
    gyro_values = {'x': 0, 'y': 0, 'z': 0}
    joycon_values = {'x': 0, 'y': 0}
    button_state = ButtonState()
    
    print("\n=== MIDI Learn Mode ===")
    print("In this mode, you'll select which controls should send MIDI data.")
    print("When you activate a control (move axis or press button),")
    print("it will start sending MIDI until you press any key.")
    
    while True:
        print_midilearn_menu()
        
        # Wait for user selection
        selection = input().strip().lower()
        if selection == 'q':
            break
            
        try:
            selection = int(selection)
            if 1 <= selection <= 6:
                options = {
                    1: ('gyro_x', "Gyro X-axis"),
                    2: ('gyro_y', "Gyro Y-axis"),
                    3: ('gyro_z', "Gyro Z-axis"),
                    4: ('joystick_x', "Joystick X-axis"),
                    5: ('joystick_y', "Joystick Y-axis"),
                    6: ('buttons', "Buttons")
                }
                control, name = options[selection]
                learn_state.current_selection = control
                print(f"\nLearning {name}... Move the control or press buttons, then press any key to stop")
                
                # Monitoring loop for the selected control
                while True:
                    # Check for keyboard input without blocking
                    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                        sys.stdin.read(1)  # Clear the input buffer
                        break
                        
                    # Process device events
                    process_devices(joycon_main, joycon_imu, gyro_values, joycon_values, button_state)
                    
                    # Send MIDI if the current selection is active
                    if should_send_midi(learn_state, gyro_values, joycon_values, button_state):
                        send_midi_for_learn(learn_state, midi_out, gyro_values, joycon_values, button_state)
                    
                    time.sleep(0.01)
                
                # After exiting monitoring, mark as learned
                learn_state.learned_mappings[control] = True
                print(f"\n{name} learning complete!")
                learn_state.current_selection = None
            else:
                print("Invalid selection. Please choose 1-6 or 'q'.")
        except ValueError:
            print("Invalid input. Please enter a number or 'q'.")
    
    print("\nMIDI Learn complete! Starting normal operation with your selections...")
    return learn_state.learned_mappings

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

def should_send_midi(learn_state, gyro_values, joycon_values, button_state):
    """Determine if we should send MIDI based on current learn state"""
    if not learn_state.current_selection:
        return False
        
    control = learn_state.current_selection
    if control == 'gyro_x' and gyro_values['x'] != 0:
        return True
    elif control == 'gyro_y' and gyro_values['y'] != 0:
        return True
    elif control == 'gyro_z' and gyro_values['z'] != 0:
        return True
    elif control == 'joystick_x' and joycon_values['x'] != 0:
        return True
    elif control == 'joystick_y' and joycon_values['y'] != 0:
        return True
    elif control == 'buttons' and any(button_state.states.values()):
        return True
        
    return False

def send_midi_for_learn(learn_state, midi_out, gyro_values, joycon_values, button_state):
    """Send MIDI for the currently learning control"""
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
    
    # Default enabled states
    gyro_enabled = not args.no_gyro
    joystick_enabled = not args.no_joystick
    
    # MIDI Learn mode overrides other settings
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
