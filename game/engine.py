# game/engine.py
import pygame
import sys
from .input_manager import InputManager
from .character import Character
from .map_loader import MapLoader
from .renderer import Renderer
from .game_state import GameState

class GameEngine:
    """Main game engine that coordinates all systems"""
    
    def __init__(self, config, characters_data):
        self.config = config
        self.characters_data = characters_data
        
        # Initialize display
        display_config = config.get('display')
        self.screen = pygame.display.set_mode((display_config['width'], display_config['height']))
        pygame.display.set_caption(display_config['title'])
        
        # Create game surface (for pixel art scaling)
        self.game_surface = pygame.Surface((
            display_config['width'] // display_config['scale_factor'],
            display_config['height'] // display_config['scale_factor']
        ))
        
        # Initialize systems
        self.input_manager = InputManager()
        self.map_loader = MapLoader()
        self.renderer = Renderer(self.game_surface, config)
        self.game_state = GameState()
        
        # Load map
        map_file = config.get('map.file', 'assets/maps/map.txt')
        self.tile_rects = self.map_loader.load_map(map_file)
        
        # Create characters
        self.characters = []
        for i, char_data in enumerate(characters_data):
            character = Character(char_data, i)
            self.characters.append(character)
            
            # Register controls
            self.input_manager.register_player(i, char_data['controls'])
        
        # Game timing
        self.clock = pygame.time.Clock()
        self.fps = display_config['fps']
        self.dt = 1.0 / self.fps
        
        # Game state
        self.running = True
    
    def run(self):
        """Main game loop"""
        while self.running:
            # Handle events
            events = pygame.event.get()
            self._handle_events(events)
            
            # Update input
            self.input_manager.update(events)
            
            # Update game state
            self._update()
            
            # Render
            self._render()
            
            # Maintain framerate
            self.clock.tick(self.fps)
        
        pygame.quit()
        sys.exit()
    
    def _handle_events(self, events):
        """Handle pygame events"""
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_RETURN:
                    if self.game_state.is_game_over():
                        self._reset_game()
    
    def _update(self):
        """Update game logic"""
        if self.game_state.is_game_over():
            return
        
        # Update characters
        for character in self.characters:
            character.update(self.dt, self.input_manager, self.config)
            character.handle_collision(self.tile_rects, self.game_surface.get_rect())
        
        # Handle combat
        self._handle_combat()
        
        # Update game state
        self._update_game_state()
    
    def _handle_combat(self):
        """Handle combat between characters"""
        for i, attacker in enumerate(self.characters):
            for j, defender in enumerate(self.characters):
                if i != j and attacker.attack_rect.colliderect(defender.rect):
                    damage = self.config.get('gameplay.damage_per_hit', 25)
                    if defender.take_damage(damage):
                        # Character died
                        defender.lives -= 1
                        if defender.lives > 0:
                            defender.health = defender.max_health
                            defender.reset_position()
                        else:
                            self.game_state.set_winner(attacker.name)
    
    def _update_game_state(self):
        """Update overall game state"""
        # Check for winner
        alive_characters = [char for char in self.characters if char.lives > 0]
        if len(alive_characters) == 1:
            self.game_state.set_winner(alive_characters[0].name)
    
    def _render(self):
        """Render the game"""
        # Clear surface
        bg_color = self.config.get('colors.background', [27, 51, 71])
        self.game_surface.fill(bg_color)
        
        # Render map
        self.renderer.draw_map(self.map_loader.game_map)
        
        # Render characters
        for character in self.characters:
            self.renderer.draw_character(character)
        
        # Render UI
        self.renderer.draw_ui(self.characters, self.game_state)
        
        # Scale and blit to main screen
        scale_factor = self.config.get('display.scale_factor', 2)
        scaled_surface = pygame.transform.scale(self.game_surface, self.screen.get_size())
        self.screen.blit(scaled_surface, (0, 0))
        
        pygame.display.flip()
    
    def _reset_game(self):
        """Reset game to initial state"""
        for character in self.characters:
            character.health = character.max_health
            character.lives = self.config.get('gameplay.max_lives', 3)
            character.reset_position()
        
        self.game_state.reset()