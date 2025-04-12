import sys
import select
import time
from mijoco.config.config_loader import ConfigLoader
from mijoco.devices.handler import ButtonState, process_devices
from mijoco.devices.detector import JoyConType
from .sender import MidiSender, send_midi_for_learn

config = ConfigLoader()

class MidiLearnState:
    def __init__(self):
        self.current_selection = None
        self.learned_mappings = {
            'gyro_x': False,
            'gyro_y': False,
            'gyro_z': False,
            'joystick_x': False,
            'joystick_y': False,
            'joystick_rx': False,
            'joystick_ry': False,
            'buttons': False
        }

def print_midilearn_menu(joycon_type: JoyConType):
    print("\nMIDI Learn Menu:")
    menu_items = []
    
    # Build filtered menu items
    for num, (control, name, control_type) in sorted(config.midi_learn_options.items()):
        if (control_type == "both" or 
            (control_type == "left" and joycon_type == JoyConType.LEFT) or
            (control_type == "right" and joycon_type == JoyConType.RIGHT)):
            menu_items.append((num, name))
    
    # Print with sequential numbering
    for i, (num, name) in enumerate(menu_items):
        print(f"{i}: {name}")
    
    print("q: Finish MIDI Learn and start normal operation")
    print("\nSelect a control to learn (0-{}) or 'q' to finish:".format(len(menu_items)-1))
    return menu_items  # Return the filtered items

# Determine if MIDI should be sent based on current control selection"""
def should_send_midi(learn_state, gyro_values, joycon_values, button_state, joycon_type: JoyConType):
    if not learn_state.current_selection:
        return False
        
    control = learn_state.current_selection
    
    # Handle joystick controls based on Joy-Con type
    if joycon_type == JoyConType.RIGHT:
        if control == 'joystick_rx' and joycon_values.get('x', 0) != 0:
            return True
        elif control == 'joystick_ry' and joycon_values.get('y', 0) != 0:
            return True
    else:  # Left Joy-Con
        if control == 'joystick_x' and joycon_values.get('x', 0) != 0:
            return True
        elif control == 'joystick_y' and joycon_values.get('y', 0) != 0:
            return True
    
    # Handle gyro controls (same for both types)
    if control.startswith('gyro'):
        axis = control.split('_')[1]
        return gyro_values.get(axis, 0) != 0
    
    # Handle buttons (same for both types)
    if control == 'buttons':
        return any(button_state.states.values())
    
    return False


def midi_learn_loop(joycon_main, joycon_imu, midi_out, joycon_type: JoyConType):
    learn_state = MidiLearnState()
    midi_sender = MidiSender(midi_out)
    gyro_values = {'x': 0, 'y': 0, 'z': 0}
    joycon_values = {'x': 0, 'y': 0}
    button_state = ButtonState()
    
    while True:
        menu_items = print_midilearn_menu(joycon_type)
        selection = input().strip().lower()
        
        if selection == 'q':
            break
            
        try:
            selection_idx = int(selection)
            if 0 <= selection_idx < len(menu_items):
                config_num = menu_items[selection_idx][0]
                control, name, _ = config.midi_learn_options[config_num]
                learn_state.current_selection = control
                print(f"\nLearning {name}... Move the control or press buttons, then press any key to stop")
                
                while True:
                    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                        sys.stdin.read(1)
                        break
                        
                    process_devices(joycon_main, joycon_imu, gyro_values, joycon_values, button_state, joycon_type)
                    
                    if should_send_midi(learn_state, gyro_values, joycon_values, button_state, joycon_type):
                        send_midi_for_learn(learn_state, midi_sender, gyro_values, joycon_values, button_state, joycon_type)
                    
                    time.sleep(0.1)
                
                learn_state.learned_mappings[control] = True
                print(f"\n{name} learning complete!")
                learn_state.current_selection = None
            else:
                print("Invalid selection. Please choose a valid number or 'q'.")
        except ValueError:
            print("Invalid input. Please enter a number or 'q'.")
    
    print("\nMIDI Learn complete! Starting normal operation with your selections...")
    return learn_state.learned_mappings
