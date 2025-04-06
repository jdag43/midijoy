# MiJoCo - JoyCon MIDI Controller

## Overview
MiJoCo transforms your Nintendo Switch JoyCon into a versatile MIDI controller, mapping its gyroscope, joystick, and buttons to MIDI CC messages for music production and live performance.

## Features
- **Motion Control**: Map gyroscope (X/Y/Z) to MIDI CC
- **Button Toggles**: Configurable CC toggles with visual feedback
- **MIDI Learn Mode**: Interactive control mapping
- **Real-time Monitoring**: Terminal display of all inputs

## Improvements potentially coming soon
- Support both joycons concurrently (for now you can only use one at a time)
- Support the Nintendo Switch Pro Controller
- Better/Configurable midi mapping for gyroscope and joystick (Cubic, deadzone etc... - for now it's simply linear)

## Requirements

- Linux kernel >= 5.16 (for hid-nintendo driver)
- `hid-nintendo` module loaded
- Python 3.8+

## Installation (Arch Linux)

```bash
git clone https://github.com/jdag43/mijoco.git
cd joycon-midi-controller
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Your user must be in the `input` usergroup (for HID events access)
```bash
sudo usermod -a -G input $USER
```

## Usage

You first need to connect the JoyCon via Bluetooth.

Then:

```bash
cd mijoco/mijoco
python main.py [--option]
```

### Options
| Key Combination | Action                                             |
|-----------------|----------------------------------------------------|
| no option       | Start with default settings (all controls enabled) |
| `--no-gyro`     | Disable gyroscope MIDI output                      |
| `--no-joystick` | Disable joystick MIDI output                       |
| `--midi-learn`  | Enter MIDI learn mode on startup                   |

### Basic Commands
```bash
# Start with default settings (all controls enabled)
python main.py

# Start with gyroscope disabled
python main.py --no-gyro

# Start with joystick disabled
python main.py --no-joystick

# Enter MIDI Learn mode
python main.py --midi-learn
```

### MIDI Learn Mode Walkthrough
1. **Start in learn mode**:
   ```bash
   python main.py --midi-learn
   ```
2. **Select controls to map**:
   ```
   MIDI Learn Menu:
   0: Gyro X-axis
   1: Gyro Y-axis
   2: Gyro Z-axis
   3: Left Joystick X-axis (if using Left JoyCon)
   4: Left Joystick Y-axis
   5: Right Joystick X-axis (if using Right JoyCon)
   6: Right Joystick Y-axis
   7: Buttons (all)
   
   Select a control to learn (0-7) or 'q' to finish:
   ```
3. **Map controls**:
   - For motion controls: Tilt/move the JoyCon
   - For joystick: Move the stick
   - For buttons: Press desired buttons
4. **Press any key** to finish mapping each control
5. **Type 'q'** when done to start normal operation

## Configuration

### 1. Selecting MIDI Output Device
When running the program, you'll be prompted to select a MIDI output:

```bash
Available MIDI outputs:
0: Midi Through Port-0
1: Virtual Raw MIDI 0-0:VirMIDI 0-0 16:0
2: ...

Enter device number (or 'q' to skip): 1
```
- Select the device number corresponding to your DAW or MIDI software
- Choose `q` to run in preview mode (no MIDI output)

### 2. Editing Control Mappings
Modify `config/config.yml` to customize the midi CC assignments:

```yaml
# Gyroscope mappings (CC values)
mappings:
  gyro:
    x: 20  # Change these numbers to desired CC
    y: 21
    z: 22

# Joystick mappings (separate for Left/Right)
  joystick_left:
    x: 23
    y: 24
  joystick_right:
    x: 25 
    y: 26

# Button mappings (button code : CC value)
  buttons:
    304: 60  # B button (Right JoyCon)
    305: 61  # A button
    309: 62  # Z button
    ...etc
```

### 3. Calibrate
Control how motion translates to MIDI values:

```yaml
input:
  gyro:
    min: -4100  # Lower bound for gyro sensitivity
    max: 4100   # Upper bound
  joystick:
    min: -32767 # Minimum joystick position
    max: 32767  # Maximum position
```

### 4. MIDI Channel Configuration
Change the MIDI channel (default 0):

```yaml
midi:
  channel: 0  # Valid values: 0-15
```

### 5. Button Behavior Customization
Configure toggle behavior:

```yaml
midi:
  toggle:
    on: 127  # Value sent when button is toggled on
    off: 0   # Value sent when toggled off
```

### Applying Changes
After modifying config.yml:
1. Save the file
2. Restart the program for changes to take effect
3. (Optional) Use `--midi-learn` to test new mappings:
```bash
python main.py --midi-learn
```