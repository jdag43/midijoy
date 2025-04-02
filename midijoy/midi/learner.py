import sys
import select
import time
from config import MIDILEARN_OPTIONS, BUTTON_NAMES, BUTTON_MAPPINGS, CC_TOGGLE_ON, CC_TOGGLE_OFF
from devices.handler import ButtonState, process_devices
from .sender import send_midi_for_learn

class MidiLearnState:
    def __init__(self):
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
    for num, (_, name) in MIDILEARN_OPTIONS.items():
        print(f"{num}: {name}")
    print("q: Finish MIDI Learn and start normal operation")
    print("\nSelect a control to learn (1-6) or 'q' to finish:")

def should_send_midi(learn_state, gyro_values, joycon_values, button_state):
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
        
        selection = input().strip().lower()
        if selection == 'q':
            break
            
        try:
            selection = int(selection)
            if selection in MIDILEARN_OPTIONS:
                control, name = MIDILEARN_OPTIONS[selection]
                learn_state.current_selection = control
                print(f"\nLearning {name}... Move the control or press buttons, then press any key to stop")
                
                while True:
                    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                        sys.stdin.read(1)
                        break
                        
                    process_devices(joycon_main, joycon_imu, gyro_values, joycon_values, button_state)
                    
                    if should_send_midi(learn_state, gyro_values, joycon_values, button_state):
                        send_midi_for_learn(learn_state, midi_out, gyro_values, joycon_values, button_state)
                    
                    time.sleep(0.01)
                
                learn_state.learned_mappings[control] = True
                print(f"\n{name} learning complete!")
                learn_state.current_selection = None
            else:
                print("Invalid selection. Please choose 1-6 or 'q'.")
        except ValueError:
            print("Invalid input. Please enter a number or 'q'.")
    
    print("\nMIDI Learn complete! Starting normal operation with your selections...")
    return learn_state.learned_mappings
