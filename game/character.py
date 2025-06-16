# game/character.py
import pygame
from enum import Enum

class CharacterState(Enum):
    IDLE = "idle"
    WALKING = "walking"
    JUMPING = "jumping"
    DUCKING = "ducking"
    ATTACKING = "attacking"

class Character(pygame.sprite.Sprite):
    """Enhanced character class with data-driven configuration"""
    
    def __init__(self, character_data, player_id):
        super().__init__()

        self.player_id = player_id
        self.name = character_data['name']
        self.spawn_pos = character_data['spawn_position']

        # Stats from config
        stats = character_data['stats']
        self.max_health = stats['health']
        self.health = self.max_health
        self.lives = stats['lives']
        self.move_speed = stats['move_speed']
        self.jump_strength = stats['jump_strength']
        self.tongue_length = stats['tongue_length']
        self.tongue_color = tuple(stats['tongue_color'])
        self.tongue_height = stats['tongue_height']

        # Images
        self.images = character_data['images']

        # Physics
        self.velocity = pygame.Vector2(0, 0)
        self.on_ground = False
        self.facing_right = True

        # State management
        self.state = CharacterState.IDLE
        self.previous_state = CharacterState.IDLE

        # Animation
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 8  # frames per animation frame

        # Combat
        self.attack_rect = pygame.Rect(0, 0, 0, 0)
        self.current_tongue_length = 0
        self.invincibility_timer = 0
        self.hit_this_frame = False

        # Input state
        self.input_state = {
            'left': False, 'right': False, 'up': False, 'down': False, 'attack': False
        }

        # Now safe to fetch current image
        self.image = self._get_current_image()
        self.rect = self.image.get_rect()
        self.rect.center = self.spawn_pos

    
    def update(self, dt, input_manager, game_config):
        """Update character state and physics"""
        # Update input state
        self._update_input_state(input_manager)
        
        # Update state machine
        self._update_state()
        
        # Apply physics
        self._apply_physics(dt, game_config)
        
        # Update animations
        self._update_animation(dt)
        
        # Update combat
        self._update_combat(dt)
        
        # Update timers
        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1
    
    def _update_input_state(self, input_manager):
        """Update input state from input manager"""
        for action in self.input_state:
            self.input_state[action] = input_manager.is_held(self.player_id, action)
    
    def _update_state(self):
        """Update character state based on input and physics"""
        self.previous_state = self.state
        
        # Priority: Attack > Duck > Jump > Walk > Idle
        if self.input_state['attack']:
            self.state = CharacterState.ATTACKING
        elif self.input_state['down'] and self.on_ground:
            self.state = CharacterState.DUCKING
            self.velocity.x = 0  # Stop horizontal movement when ducking
        elif not self.on_ground:
            self.state = CharacterState.JUMPING
        elif self.input_state['left'] or self.input_state['right']:
            self.state = CharacterState.WALKING
        else:
            self.state = CharacterState.IDLE
        
        # Update facing direction
        if self.input_state['right'] and self.state != CharacterState.DUCKING:
            self.facing_right = True
        elif self.input_state['left'] and self.state != CharacterState.DUCKING:
            self.facing_right = False
    
    def _apply_physics(self, dt, game_config):
        """Apply physics and movement"""
        gravity = game_config.get('gameplay.gravity', 0.3)
        max_fall_speed = game_config.get('gameplay.max_fall_speed', 4)
        
        # Horizontal movement
        if self.state != CharacterState.DUCKING and self.state != CharacterState.ATTACKING:
            if self.input_state['left']:
                self.velocity.x = -self.move_speed
            elif self.input_state['right']:
                self.velocity.x = self.move_speed
            else:
                self.velocity.x = 0
        
        # Jumping
        if self.input_state['up'] and self.on_ground and self.state != CharacterState.DUCKING:
            self.velocity.y = self.jump_strength
            self.on_ground = False
        
        # Apply gravity
        if not self.on_ground:
            self.velocity.y += gravity
            if self.velocity.y > max_fall_speed:
                self.velocity.y = max_fall_speed
    
    def _update_animation(self, dt):
        """Update character animations"""
        self.animation_timer += 1
        
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            
            # Get animation frames for current state
            frames = self._get_animation_frames()
            if frames:
                self.animation_frame = (self.animation_frame + 1) % len(frames)
        
        # Update image
        self.image = self._get_current_image()
    
    def _get_animation_frames(self):
        """Get animation frames for current state"""
        direction = "right" if self.facing_right else "left"
        
        if self.state == CharacterState.WALKING:
            return self.images.get('walking', {}).get(direction, [])
        elif self.state == CharacterState.ATTACKING:
            return [self.images.get('attacking', {}).get(direction)]
        elif self.state == CharacterState.DUCKING:
            return [self.images.get('ducking')]
        else:  # IDLE or JUMPING
            return [self.images.get('idle', {}).get(direction)]
    
    def _get_current_image(self):
        """Get current image based on state and animation frame"""
        frames = self._get_animation_frames()
        if frames and len(frames) > 0:
            frame_index = min(self.animation_frame, len(frames) - 1)
            return frames[frame_index]
        
        # Fallback to a basic surface
        surface = pygame.Surface((32, 32))
        surface.fill((255, 0, 255))  # Magenta placeholder
        return surface
    
    def _update_combat(self, dt):
        """Update combat-related logic"""
        if self.state == CharacterState.ATTACKING:
            # Extend tongue
            if self.current_tongue_length < self.tongue_length:
                self.current_tongue_length += 3
            
            # Update attack rect
            if self.facing_right:
                self.attack_rect = pygame.Rect(
                    self.rect.centerx, self.rect.centery - 1,
                    self.current_tongue_length, self.tongue_height
                )
            else:
                self.attack_rect = pygame.Rect(
                    self.rect.centerx - self.current_tongue_length, self.rect.centery - 1,
                    self.current_tongue_length, self.tongue_height
                )
        else:
            # Retract tongue
            self.current_tongue_length = 0
            self.attack_rect = pygame.Rect(0, 0, 0, 0)
    
    def handle_collision(self, tiles, screen_rect):
        """Handle collision with tiles and screen boundaries"""
        # Keep player on screen
        self.rect.clamp_ip(screen_rect)
        
        # Move horizontally first
        self.rect.x += self.velocity.x
        
        # Check horizontal collisions
        hit_list = [tile for tile in tiles if self.rect.colliderect(tile)]
        for tile in hit_list:
            if self.velocity.x > 0:  # Moving right
                self.rect.right = tile.left
            elif self.velocity.x < 0:  # Moving left
                self.rect.left = tile.right
        
        # Move vertically
        self.rect.y += self.velocity.y
        
        # Check vertical collisions
        hit_list = [tile for tile in tiles if self.rect.colliderect(tile)]
        self.on_ground = False
        
        for tile in hit_list:
            if self.velocity.y > 0:  # Falling
                self.rect.bottom = tile.top
                self.velocity.y = 0
                self.on_ground = True
            elif self.velocity.y < 0:  # Jumping up
                self.rect.top = tile.bottom
                self.velocity.y = 0
    
    def draw_attack(self, surface):
        """Draw the character's attack (tongue)"""
        if self.state == CharacterState.ATTACKING and self.current_tongue_length > 0:
            pygame.draw.rect(surface, self.tongue_color, self.attack_rect)
    
    def take_damage(self, damage):
        """Apply damage to character"""
        if self.invincibility_timer <= 0 and self.state != CharacterState.DUCKING:
            self.health -= damage
            self.invincibility_timer = 60  # 1 second at 60 FPS
            self.hit_this_frame = True
            
            if self.health <= 0:
                self.health = 0
                return True  # Character died
        return False
    
    def reset_position(self):
        """Reset character to spawn position"""
        self.rect.center = self.spawn_pos
        self.velocity = pygame.Vector2(0, 0)
        self.state = CharacterState.IDLE
