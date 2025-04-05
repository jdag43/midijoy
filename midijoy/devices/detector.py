import evdev
import mido
       

def find_joycon():
    """Find and return Joy-Con devices with haptic feedback"""
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
