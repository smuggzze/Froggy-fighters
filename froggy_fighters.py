# froggy_fighters.py
import pygame
import sys
import json
import os
from pathlib import Path

from game.engine import GameEngine
from game.config import GameConfig
from game.character_loader import CharacterLoader

def main():
    """Main entry point for Froggy Fighters"""
    pygame.init()
    
    # Load game configuration
    config = GameConfig()
    
    # Load character data
    character_loader = CharacterLoader()
    characters_data = character_loader.load_all_characters()
    
    if len(characters_data) < 2:
        print("Error: Need at least 2 characters to play!")
        sys.exit(1)
    
    # Initialize game engine
    engine = GameEngine(config, characters_data)
    
    # Run the game
    engine.run()

if __name__ == "__main__":
    main()