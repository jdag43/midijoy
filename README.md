# MidiJoy

## Overview
Transform your Nintendo Switch JoyCon into an unusual MIDI controller.

## Current Features
- **Gyroscope Control**: Maps X/Y/Z axes to MIDI CC (default: CC20-22)
- **Joystick Control**: Maps X/Y axes to MIDI CC (default: CC23-24)
- **Button Toggles**: 11 buttons mapped to toggle CC values (default: CC60-70)
- **MIDI Learn Mode**: Interactive control mapping (`--midi-learn` flag)
- **Real-time Feedback**: Terminal display of active controls

## Requirements
- Nintendo Switch JoyCon (Left) **only** (right coming soon)
- Linux system with:
  - Bluetooth support
  - Linux kernel >= 5.16 (for hid-nintendo driver)
  - hid-nintendo module loaded
  - Python 3.8+

## Installation
```bash
# 1. Install dependencies
sudo apt-get install python3 python3-pip python3-dev libevdev2

# 2. Set up project
git clone https://github.com/yourusername/joycon-midi-controller.git
cd joycon-midi-controller
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
