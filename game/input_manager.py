# game/input_manager.py
import pygame

class InputManager:
    """Handles input mapping and state management"""
    
    def __init__(self):
        self.key_map = self._build_key_map()
        self.player_inputs = {}
    
    def _build_key_map(self):
        """Build mapping from string names to pygame key constants"""
        return {
            'a': pygame.K_a, 'b': pygame.K_b, 'c': pygame.K_c, 'd': pygame.K_d,
            'e': pygame.K_e, 'f': pygame.K_f, 'g': pygame.K_g, 'h': pygame.K_h,
            'i': pygame.K_i, 'j': pygame.K_j, 'k': pygame.K_k, 'l': pygame.K_l,
            'm': pygame.K_m, 'n': pygame.K_n, 'o': pygame.K_o, 'p': pygame.K_p,
            'q': pygame.K_q, 'r': pygame.K_r, 's': pygame.K_s, 't': pygame.K_t,
            'u': pygame.K_u, 'v': pygame.K_v, 'w': pygame.K_w, 'x': pygame.K_x,
            'y': pygame.K_y, 'z': pygame.K_z,
            'left': pygame.K_LEFT, 'right': pygame.K_RIGHT,
            'up': pygame.K_UP, 'down': pygame.K_DOWN,
            'space': pygame.K_SPACE, 'enter': pygame.K_RETURN,
            'lshift': pygame.K_LSHIFT, 'rshift': pygame.K_RSHIFT,
            'lctrl': pygame.K_LCTRL, 'rctrl': pygame.K_RCTRL,
        }
    
    def register_player(self, player_id, controls_config):
        """Register a player's control scheme"""
        self.player_inputs[player_id] = {
            'keys': {action: self.key_map.get(key.lower(), pygame.K_UNKNOWN) 
                    for action, key in controls_config.items()},
            'state': {action: False for action in controls_config.keys()},
            'pressed': {action: False for action in controls_config.keys()},
            'released': {action: False for action in controls_config.keys()}
        }
    
    def update(self, events):
        """Update input state based on events"""
        # Reset frame-specific states
        for player_id in self.player_inputs:
            for action in self.player_inputs[player_id]['pressed']:
                self.player_inputs[player_id]['pressed'][action] = False
                self.player_inputs[player_id]['released'][action] = False
        
        # Process events
        for event in events:
            if event.type == pygame.KEYDOWN:
                self._handle_key_down(event.key)
            elif event.type == pygame.KEYUP:
                self._handle_key_up(event.key)
    
    def _handle_key_down(self, key):
        """Handle key press events"""
        for player_id, input_data in self.player_inputs.items():
            for action, mapped_key in input_data['keys'].items():
                if key == mapped_key and not input_data['state'][action]:
                    input_data['state'][action] = True
                    input_data['pressed'][action] = True
    
    def _handle_key_up(self, key):
        """Handle key release events"""
        for player_id, input_data in self.player_inputs.items():
            for action, mapped_key in input_data['keys'].items():
                if key == mapped_key and input_data['state'][action]:
                    input_data['state'][action] = False
                    input_data['released'][action] = True
    
    def is_pressed(self, player_id, action):
        """Check if action was just pressed this frame"""
        return self.player_inputs.get(player_id, {}).get('pressed', {}).get(action, False)
    
    def is_held(self, player_id, action):
        """Check if action is currently held down"""
        return self.player_inputs.get(player_id, {}).get('state', {}).get(action, False)
    
    def is_released(self, player_id, action):
        """Check if action was just released this frame"""
        return self.player_inputs.get(player_id, {}).get('released', {}).get(action, False)