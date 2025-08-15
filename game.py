import pygame
import random

import scripts.pgtools as pt

from scripts.player import Player
from scripts.hud import HUD


class Game:
    def __init__(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode((1080, 720))
        self.display = pygame.Surface((270, 180))
        self.ui_display = pygame.Surface(self.display.get_size(), pygame.SRCALPHA)
        pygame.display.set_caption('turnip escape')
        self.clock = pygame.time.Clock()
        
        self.animations = pt.AnimationManager()
        self.tilemap = pt.Tilemap(self, self.display.get_size(), tile_size=8)
        self.tilemap.load_map('data/maps/test_1.json')
        
        self.input = pt.Input() 
        self.vfx = pt.VFX(self)
        self.font = pt.Font()
        self.particle_manager = pt.ParticleManager()
        
        player_pos = self.tilemap.extract(lambda x: x['type'] == 'spawners', False, False)[0]['pos']
        
        self.camera = pt.Camera(self.display.get_size(), lag=6)
        self.player = Player(self, player_pos, (4, 9))
        self.camera.set_target(self.player)
        
        self.hud = HUD(self)
        
        self.master_clock = 0
        
        self.particles = []
        
    def run(self):
        while True:
            
            self.master_clock += 1
            
            self.display.fill((21, 17, 26))
            self.ui_display.fill((0, 0, 0, 0))
            
            self.camera.update()

            self.tilemap.render_visible(self.display, self.camera.pos)
            
            self.player.update()
            self.player.render(self.display, self.camera.pos)
            
            self.input.update()
            
            self.hud.render(self.ui_display, self.camera.pos)
                                    
            self.vfx.update(1/60)
            self.vfx.render(self.display, self.camera.pos)
            
            self.particle_manager.update(1/60)
            self.particle_manager.render(self.display, self.camera.pos)
            
            for torch in self.tilemap.extract(lambda x: x['type'] == 'test' and x['variant'] == 0):
                pt.utils.glow_blit(self.display, loc=(torch['pos'][0] - self.camera.pos[0] - 15 + 5, torch['pos'][1] - self.camera.pos[1] - 15 + 3), radius=15, glow_color=(3, 7, 23))
                pt.utils.glow_blit(self.display, loc=(torch['pos'][0] - self.camera.pos[0] - 27 + 5, torch['pos'][1] - self.camera.pos[1] - 27 + 3), radius=27, glow_color=(3, 7, 23))
                if random.randint(1, 2) == 1:
                    self.particle_manager.particles.append(pt.Particle(self, (torch['pos'][0] + 5, torch['pos'][1] + 3), (10 + random.random() * -20, -10 + random.random() * -8), 'particles', decay_rate=1.2 + random.random(), start_frame=3 + random.random() * 2, glow=(3, 3 + random.randint(1, 3), 11 + random.randint(1, 6)), glow_radius=5 + random.random() * 6))
                
                    
                    
            self.display.blit(self.ui_display, (0, 0))
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

if __name__ == '__main__':
    Game().run()