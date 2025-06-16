
# game/renderer.py
import pygame

class Renderer:
    def __init__(self, surface, config):
        self.surface = surface
        self.config = config
        self.font = pygame.font.Font(None, 24)
        self.health_bar_width = 100
        self.health_bar_height = 10

    def draw_map(self, game_map):
        tile_size = self.config.get("map.tile_size", 16)
        for y, row in enumerate(game_map):
            for x, tile in enumerate(row):
                if tile == '1':
                    pygame.draw.rect(self.surface, (100, 100, 100), (x * tile_size, y * tile_size, tile_size, tile_size))
                elif tile == '2':
                    pygame.draw.rect(self.surface, (150, 150, 150), (x * tile_size, y * tile_size, tile_size, tile_size))

    def draw_character(self, character):
        self.surface.blit(character.image, character.rect)
        character.draw_attack(self.surface)

    def draw_ui(self, characters, game_state):
        for i, char in enumerate(characters):
            x = 10 if i == 0 else self.surface.get_width() - 110
            y = 10
            self._draw_health_bar(char, x, y)
            self._draw_lives(char, x, y + 15)

        if game_state.is_game_over():
            self._draw_winner_screen(game_state.winner_name)

    def _draw_health_bar(self, character, x, y):
        pygame.draw.rect(self.surface, (255, 255, 255), (x, y, self.health_bar_width, self.health_bar_height), 1)
        fill_width = int(self.health_bar_width * (character.health / character.max_health))
        pygame.draw.rect(self.surface, (255, 0, 0), (x, y, fill_width, self.health_bar_height))

    def _draw_lives(self, character, x, y):
        lives_text = self.font.render(f"Lives: {character.lives}", True, (255, 255, 255))
        self.surface.blit(lives_text, (x, y))

    def _draw_winner_screen(self, winner_name):
        width, height = self.surface.get_size()
        overlay = pygame.Surface((width, height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.surface.blit(overlay, (0, 0))

        win_text = self.font.render(f"{winner_name} Wins! Press Enter to restart.", True, (255, 255, 255))
        self.surface.blit(win_text, (width // 2 - win_text.get_width() // 2, height // 2))

