import sys
import yaml
from pathlib import Path
from typing import Dict, Any, Tuple
from enum import Enum

class JoyConType(Enum):
    LEFT = "Left"
    RIGHT = "Right"

class UIConfig:
    """Hardcoded UI configuration that was previously in ui.yml"""
    MIDI_LEARN_OPTIONS = {
        0: ("gyro_x", "Gyro X-axis", "both"),
        1: ("gyro_y", "Gyro Y-axis", "both"),
        2: ("gyro_z", "Gyro Z-axis", "both"),
        3: ("joystick_x", "Left Joystick X-axis", "left"),
        4: ("joystick_y", "Left Joystick Y-axis", "left"),
        5: ("joystick_rx", "Right Joystick X-axis", "right"),
        6: ("joystick_ry", "Right Joystick Y-axis", "right"),
        7: ("buttons", "Buttons (all)", "both")
    }

    BUTTON_NAMES = {
        # Left Joy-Con buttons
        309: "Z (L)",
        314: "- (L)",
        317: "THUMB (L)",
        544: "↑ (L)",
        545: "↓ (L)",
        546: "← (L)",
        547: "→ (L)",
        # Right Joy-Con buttons
        304: "B (R)",
        305: "A (R)",
        307: "X (R)",
        308: "Y (R)",
        315: "+ (R)",
        316: "MODE (R)",
        318: "THUMB (R)",
        # Common Joy-Con buttons
        310: "TL",
        311: "TR",
        312: "TL2",
        313: "TR2"
    }

class ConfigLoader:
    def __init__(self):
        # Determine paths
        self.is_frozen = getattr(sys, 'frozen', False)
        self.base_dir = Path(sys.executable).parent if self.is_frozen else Path(__file__).parent.parent.parent
        
        # Load configurations
        self.user_config = self._load_user_config()
        self.ui_config = {
            'midi_learn': UIConfig.MIDI_LEARN_OPTIONS,
            'button_names': UIConfig.BUTTON_NAMES
        }
        self._init_defaults()

    def _load_user_config(self) -> Dict[str, Any]:
        """Load user-editable config.yml from executable directory"""
        config_path = self.base_dir / "config.yml"
        if not config_path.exists():
            raise FileNotFoundError(
                f"Required config.yml not found at: {config_path}\n"
                "Please place it in the same directory as the executable."
            )
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f) or {}

    def _init_defaults(self):
        """Initialize default values for critical settings"""
        self.user_config.setdefault('midi', {}).update({
            'channel': self.user_config['midi'].get('channel', 0),
            'toggle': {
                'on': self.user_config['midi'].get('toggle', {}).get('on', 127),
                'off': self.user_config['midi'].get('toggle', {}).get('off', 0)
            }
        })

    @property
    def config(self) -> Dict[str, Any]:
        return {**self.user_config, **self.ui_config}

    @property
    def gyro_range(self) -> tuple:
        return (self.user_config['input']['gyro']['min'], 
                self.user_config['input']['gyro']['max'])

    @property
    def joystick_range(self) -> tuple:
        return (self.user_config['input']['joystick']['min'], 
                self.user_config['input']['joystick']['max'])

    @property
    def button_mappings(self) -> Dict[int, int]:
        return self.user_config['mappings']['buttons']

    @property
    def gyro_cc_map(self) -> Dict[str, int]:
        return self.user_config['mappings']['gyro']

    @property
    def joystick_left_cc_map(self) -> Dict[str, int]:
        return self.user_config['mappings']['joystick_left']

    @property
    def joystick_right_cc_map(self) -> Dict[str, int]:
        return self.user_config['mappings']['joystick_right']

    @property
    def button_names(self) -> Dict[int, str]:
        return self.ui_config['button_names']

    @property
    def midi_learn_options(self) -> Dict[int, tuple]:
        return UIConfig.MIDI_LEARN_OPTIONS