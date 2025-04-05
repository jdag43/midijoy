import yaml
from pathlib import Path
from typing import Dict, Any

class ConfigLoader:
    def __init__(self, config_path: str = "config/config.yml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    @property
    def gyro_range(self) -> tuple:
        return (self.config['input']['gyro']['min'], 
                self.config['input']['gyro']['max'])

    @property
    def joystick_range(self) -> tuple:
        return (self.config['input']['joystick']['min'], 
                self.config['input']['joystick']['max'])

    @property
    def button_mappings(self) -> Dict[int, int]:
        return self.config['mappings']['buttons']

    @property
    def gyro_cc_map(self) -> Dict[str, int]:
        return self.config['mappings']['gyro']

    @property
    def joystick_cc_map(self) -> Dict[str, int]:
        return self.config['mappings']['joystick']

    @property
    def button_names(self) -> Dict[int, str]:
        return self.config['button_names']

    @property
    def midi_learn_options(self) -> Dict[int, tuple]:
        return {k: tuple(v) for k, v in self.config['midi_learn'].items()}