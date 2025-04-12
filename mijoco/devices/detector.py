import evdev
import mido
from mijoco.config.config_loader import JoyConType  # Now using centralized enum

def find_joycon():
    print("\nSearching for Joy-Con devices...")
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    
    joycon_main = None
    joycon_imu = None
    joycon_type = None
    
    for device in devices:
        name = device.name
        if "Joy-Con (L)" in name:
            if "(IMU)" in name:
                joycon_imu = device
                print(f"Found Left Joy-Con IMU: {name} at {device.path}")
            else:
                joycon_main = device
                joycon_type = JoyConType.LEFT
                print(f"Found Left Joy-Con Main: {name} at {device.path}")
        elif "Joy-Con (R)" in name:
            if "(IMU)" in name:
                joycon_imu = device
                print(f"Found Right Joy-Con IMU: {name} at {device.path}")
            else:
                joycon_main = device
                joycon_type = JoyConType.RIGHT
                print(f"Found Right Joy-Con Main: {name} at {device.path}")

    if not joycon_main or not joycon_imu or not joycon_type:
        print("\nError: Could not find required Joy-Con devices!")
        if not joycon_main:
            print("- Main Joy-Con device missing")
        if not joycon_imu:
            print("- IMU Joy-Con device missing")
        print("Available devices:")
        for i, device in enumerate(devices):
            print(f"  {i}: {device.path} - {device.name}")
        return None, None, None
    
    print(f"\n{joycon_type.value} Joy-Con successfully detected!")
    return joycon_main, joycon_imu, joycon_type

def select_midi_output():
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