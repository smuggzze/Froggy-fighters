# game/character_loader.py
import json
import pygame
import os
from pathlib import Path

class CharacterLoader:
    """Loads character data from JSON configuration files"""
    
    def __init__(self, characters_dir="config/characters"):
        self.characters_dir = Path(characters_dir)
        self.loaded_characters = {}
    
    def load_all_characters(self):
        """Load all character configurations"""
        characters = []
        
        if not self.characters_dir.exists():
            print(f"Characters directory {self.characters_dir} not found!")
            return self._create_default_characters()
        
        for char_file in self.characters_dir.glob("*.json"):
            try:
                character_data = self.load_character(char_file)
                if character_data:
                    characters.append(character_data)
            except Exception as e:
                print(f"Error loading character {char_file}: {e}")
        
        if len(characters) < 2:
            print("Not enough characters found, using defaults")
            return self._create_default_characters()
        
        return characters[:2]  # Return first 2 characters for now
    
    def load_character(self, config_file):
        """Load a single character from JSON file"""
        with open(config_file, 'r') as f:
            char_data = json.load(f)
        
        # Load and process images
        char_data['images'] = self._load_character_images(char_data['assets'])
        
        return char_data
    
    def _load_character_images(self, assets_config):
        """Load all images for a character"""
        images = {}
        
        for category, paths in assets_config.items():
            if isinstance(paths, str):
                # Single image
                images[category] = self._load_image(paths)
            elif isinstance(paths, list):
                # Multiple images (animation frames)
                images[category] = [self._load_image(path) for path in paths]
            elif isinstance(paths, dict):
                # Nested structure (e.g., walking_left, walking_right)
                images[category] = {}
                for sub_category, sub_paths in paths.items():
                    if isinstance(sub_paths, list):
                        images[category][sub_category] = [self._load_image(path) for path in sub_paths]
                    else:
                        images[category][sub_category] = self._load_image(sub_paths)
        
        return images
    
    def _load_image(self, path):
        """Load a single image from path directly (no hardcoded prepends)"""
        try:
            image = pygame.image.load(path)
            image.set_colorkey((255, 255, 255))  # Remove white background
            return image
        except pygame.error as e:
            print(f"Could not load image {path}: {e}")
            surface = pygame.Surface((32, 32))
            surface.fill((255, 0, 255))  # Magenta placeholder
            return surface

    
    def _create_default_characters(self):
        """Create default character configurations if files are missing"""
        return [
            {
                "name": "Green Froggy",
                "spawn_position": [200, 100],
                "controls": {
                    "left": "a",
                    "right": "d", 
                    "up": "w",
                    "down": "s",
                    "attack": "lshift"
                },
                "stats": {
                    "health": 100,
                    "lives": 3,
                    "move_speed": 2,
                    "jump_strength": -5,
                    "tongue_length": 50,
                    "tongue_color": [172, 61, 177],
                    "tongue_height": 3
                },
                "images": self._create_placeholder_images("green"),
                "assets": {}
            },
            {
                "name": "Pink Froggy", 
                "spawn_position": [500, 100],
                "controls": {
                    "left": "left",
                    "right": "right",
                    "up": "up", 
                    "down": "down",
                    "attack": "rshift"
                },
                "stats": {
                    "health": 100,
                    "lives": 3,
                    "move_speed": 2,
                    "jump_strength": -5,
                    "tongue_length": 50,
                    "tongue_color": [11, 205, 221],
                    "tongue_height": 3
                },
                "images": self._create_placeholder_images("pink"),
                "assets": {}
            }
        ]
    
    def _create_placeholder_images(self, color_name):
        """Create placeholder images for testing"""
        color_map = {
            "green": (0, 255, 0),
            "pink": (255, 192, 203)
        }
        color = color_map.get(color_name, (255, 0, 255))
        
        # Create basic placeholder images
        base_surface = pygame.Surface((32, 32))
        base_surface.fill(color)
        
        return {
            "idle": {"left": base_surface.copy(), "right": base_surface.copy()},
            "walking": {
                "left": [base_surface.copy(), base_surface.copy()],
                "right": [base_surface.copy(), base_surface.copy()]
            },
            "attacking": {"left": base_surface.copy(), "right": base_surface.copy()},
            "ducking": base_surface.copy()
        }
