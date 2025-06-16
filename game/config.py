# game/config.py
import json
import os
from pathlib import Path

class GameConfig:
    """Centralized game configuration"""
    
    def __init__(self, config_file="config/game_config.json"):
        self.config_file = config_file
        self.load_config()
    
    def load_config(self):
        """Load configuration from JSON file"""
        default_config = {
            "display": {
                "width": 1377,
                "height": 705,
                "title": "Froggy Fighters",
                "fps": 60,
                "scale_factor": 2
            },
            "gameplay": {
                "gravity": 0.3,
                "max_fall_speed": 4,
                "jump_strength": -5,
                "move_speed": 2,
                "invincibility_frames": 60,
                "max_lives": 3,
                "max_health": 100,
                "damage_per_hit": 25
            },
            "colors": {
                "background": [27, 51, 71],
                "white": [255, 255, 255],
                "black": [0, 0, 0],
                "red": [255, 0, 0],
                "green": [10, 161, 126],
                "pink": [245, 94, 129]
            },
            "map": {
                "file": "assets/maps/map.txt",
                "tile_size": 16
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    self._merge_config(default_config, loaded_config)
            
            self.config = default_config
            
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = default_config
    
    def _merge_config(self, default, loaded):
        """Recursively merge loaded config with defaults"""
        for key, value in loaded.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self._merge_config(default[key], value)
                else:
                    default[key] = value
    
    def get(self, path, default=None):
        """Get config value using dot notation (e.g., 'display.width')"""
        keys = path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value