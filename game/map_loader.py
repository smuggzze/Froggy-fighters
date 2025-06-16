import os
import pygame

class MapLoader:
    def __init__(self):
        self.game_map = []
        self.tile_size = 16

        tile_dir = os.path.join("assets", "tiles")
        tile1_path = os.path.join(tile_dir, "test_block1.png")
        tile2_path = os.path.join(tile_dir, "test_block2.png")

        try:
            self.block_1 = pygame.image.load(tile1_path).convert()
            self.block_2 = pygame.image.load(tile2_path).convert()
            
        except pygame.error as e:
            print(f"Error loading tiles: {e}")
            self.block_1 = pygame.Surface((self.tile_size, self.tile_size))
            self.block_1.fill((100, 100, 100))
            self.block_2 = pygame.Surface((self.tile_size, self.tile_size))
            self.block_2.fill((150, 150, 150))

    
    def load_map(self, map_file):
        """Load map from file and return collision rects"""
        tile_rects = []
        
        try:
            with open(map_file, 'r') as file:
                data = file.read().strip().split('\n')
                self.game_map = [list(row) for row in data]
        except FileNotFoundError:
            print(f"Map file {map_file} not found, creating default map")
            self.game_map = self._create_default_map()
        
        # Generate collision rects
        for y, row in enumerate(self.game_map):
            for x, tile in enumerate(row):
                if tile != '0':
                    rect = pygame.Rect(x * self.tile_size, y * self.tile_size, 
                                     self.tile_size, self.tile_size)
                    tile_rects.append(rect)
        
        return tile_rects
    
    def _create_default_map(self):
        """Create a simple default map"""
        width, height = 40, 20
        game_map = [['0' for _ in range(width)] for _ in range(height)]
        
        # Add ground
        for x in range(width):
            game_map[height-1][x] = '1'
            game_map[height-2][x] = '2'
        
        return game_map
