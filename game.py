import pygame
import random
import math

import scripts.pgtools as pt

from scripts.player import Player
from scripts.key import Key
from scripts.hud import HUD

RESOLUTION = (240, 160)
RENDER_SCALE = 3
TILE_SIZE = 8
TILE_EXTRACTS = {
    'player': lambda x: x['type'] == 'spawners' and x['variant'] == 0,
    'torch': lambda x: x['type'] == 'test' and x['variant'] == 0,
    'key': lambda x: x['type'] == 'spawners' and x['variant'] == 1,
    'door': lambda x: x['type'] == 'spawners' and x['variant'] == 2,
    'rocks': lambda x: x['type'] == 'decor' and x['variant'] in [0, 1]
}
PLAYER_SIZE = (4, 7)

class Game:
    def __init__(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode((RESOLUTION[0] * RENDER_SCALE, RESOLUTION[1] * RENDER_SCALE))
        self.display = pygame.Surface((RESOLUTION[0], RESOLUTION[1]))
        self.ui_display = pygame.Surface(self.display.get_size(), pygame.SRCALPHA)
        pygame.display.set_caption('turnip escape')
        self.clock = pygame.time.Clock()
        
        self.animations = pt.AnimationManager()
        self.tilemap = pt.Tilemap(self, tile_size=TILE_SIZE)            
        self.input = pt.Input(RENDER_SCALE) 
        self.vfx = pt.VFX(self)
        self.particle_manager = pt.ParticleManager()
        self.camera = pt.Camera(self.display.get_size(), lag=20)
        self.hud = HUD(self)
        
        self.misc_images = pt.utils.load_imgs_dict('data/images/misc')
        
        self.master_clock = 0
        self.dt = 0.1
        self.level = 0
        
        self.load_level(self.level)
        
    
    def spawn_keys(self):
        self.keys = []
        keys = self.tilemap.extract(TILE_EXTRACTS['key'], False, True)
        for key in keys:
            self.keys.append(Key(self, key['pos'], (5, 9)))
    
    def load_level(self, level):
        self.tilemap.load_map('data//maps/test_2.json')
        # self.tilemap.load_map(f'data/maps/map_{level}.json')
        
        self.transition = -50
        self.keys_collected = 0
        self.door_entered = False

        self.player = Player(self, self.tilemap.extract(TILE_EXTRACTS['player'], False, False)[0]['pos'], PLAYER_SIZE)
        self.rocks = self.tilemap.extract(TILE_EXTRACTS['rocks'], True)
        self.camera.set_target(self.player)
        self.spawn_keys()
        
        self.rock_sparks = []
        self.vfx.reset()
        self.particle_manager.reset()
    
    def rock_collision_sparks(self, spark):
        if self.tilemap.tile_collide(spark.pos.copy()):
            for i in range(4):
                angle = math.radians(random.uniform(15, 165)) - math.pi
                speed = 60 + random.random() * 30
                decay_rate = 300 + random.random() * 40
                self.vfx.sparks.append(pt.Spark(spark.pos,  angle, speed, decay_rate))
            return True
        if self.player.rect.collidepoint(spark.pos):
            self.player.die()
        
     
    def run(self):
        while True:
            self.master_clock += 1
            
            if self.transition != 0:
                self.transition =  min(self.transition + 1, 50)
                if (self.transition >= 50) and (self.player.pos[1] >= self.camera.scroll[1] + self.display.get_height()) and (self.player.dead):
                    self.load_level(self.level)
                if (self.transition >= 50) and self.door_entered:
                    self.level += 1
                    self.load_level(self.level)
            
            self.display.fill((8, 20, 30))
            self.ui_display.fill((0, 0, 0, 0))

            self.camera.update()
            
            edges = self.tilemap.get_map_edges()
            
            
            # if self.camera.scroll[0] < edges[0]:
            #     self.camera.scroll[0] = edges[0]
            # if self.camera.scroll[0] > edges[1] - self.display.get_width():
            #     self.camera.scroll[0] = edges[1] - self.display.get_width()
            # if self.camera.scroll[1] < edges[2]:
            #     self.camera.scroll[1] = edges[2]
            # if self.camera.scroll[1] > edges[3] - self.display.get_height():
            #     self.camera.scroll[1] = edges[3] - self.display.get_height()
                          
            self.tilemap.render_visible(self.display, offset=self.camera.render_scroll)
            
            for key in self.keys:
                key.update(self.dt)
                key.render(self.display, offset=self.camera.render_scroll)
            
            for rock_spark in self.rock_sparks:
                kill = self.rock_collision_sparks(rock_spark)
                kill = kill or rock_spark.update(self.dt) 
                rock_spark.render(self.display, self.camera.render_scroll)
                if kill:
                    self.rock_sparks.remove(rock_spark)
            
            for torch in self.tilemap.extract(TILE_EXTRACTS['torch'], True):
                pt.utils.glow_blit(self.display, loc=(torch['pos'][0] - self.camera.pos[0] - 15 + 5, torch['pos'][1] - self.camera.pos[1] - 15 + 3), radius=15, glow_color=(3, 7, 23))
                pt.utils.glow_blit(self.display, loc=(torch['pos'][0] - self.camera.pos[0] - 27 + 5, torch['pos'][1] - self.camera.pos[1] - 27 + 3), radius=27, glow_color=(3, 7, 23))
                self.particle_manager.particles.append(pt.Particle(self, (torch['pos'][0] + 5, torch['pos'][1] + 3), (4 + random.random() * -8, -4 + random.random() * -8), 'particles', decay_rate=1.7 + random.random(), start_frame=2 + random.random() * 3, glow=(3, 3 + random.randint(1, 3), 8 + random.randint(1, 6)), glow_radius=3 + random.random() * 6))

            self.player.update()
            self.player.render(self.display, offset=self.camera.render_scroll)
             
            self.hud.render(self.ui_display, offset=self.camera.render_scroll)
                                    
            self.vfx.update(self.dt)
            self.vfx.render(self.display, offset=self.camera.render_scroll)
            
            self.particle_manager.update(self.dt)
            self.particle_manager.render(self.display, self.camera.pos)
            
            self.input.update()
                        
            door = self.tilemap.extract(TILE_EXTRACTS['door'], True)
            if door:
                door = door[0]
                door_rect = pygame.Rect(door['pos'][0], door['pos'][1], 7, 11)
                if (self.player.rect.collidepoint(door_rect.center)) and (self.transition == 0) and (self.keys_collected == len(self.keys)):
                    self.transition = max(self.transition, 1)
                    self.door_entered = True
            

            for rock in self.rocks:
                img_size = self.tilemap.tiles[rock['type']][rock['variant']].get_size()
                rock_collide_check = (rock['pos'][0] + random.random() * img_size[0], rock['pos'][1] + img_size[1])
                if not self.tilemap.tile_collide(rock_collide_check):
                    if random.randint(1, 100) == 1:
                        angle = math.radians(90)
                        speed = 40 + random.random() * 20
                        decay_rate = 3 + random.random()
                        self.rock_sparks.append(pt.Spark(rock_collide_check, angle, speed, decay_rate, custom_color=(47, 91, 128)))
                        
            
            if self.transition:
                black_surf = pygame.Surface(self.display.get_size())
                black_surf.set_alpha(abs(self.transition) / 50 * 255)
                self.display.blit(black_surf, (0, 0))
            
            
            self.display.blit(self.ui_display, (0, 0))
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.dt = self.clock.tick(60) / 1000
            
            pygame.display.set_caption(str(round(self.clock.get_fps(), 1)))
            

if __name__ == '__main__':
    
    Game().run()