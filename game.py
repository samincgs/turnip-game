import pygame
import random
import math

import scripts.pgtools as pt

from scripts.player import Player
from scripts.key import Key
from scripts.hud import HUD
from scripts.turret import Turret
from scripts.mole import Mole

RESOLUTION = (240, 160)
RENDER_SCALE = 3
TILE_SIZE = 8
PLAYER_SIZE = (4, 8)

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
        self.camera = pt.Camera(self.display.get_size(), tile_size=TILE_SIZE, lag=20)
        self.hud = HUD(self)
        
        self.misc_images = pt.utils.load_imgs_dict('data/images/misc')
        self.fallen_rock_imgs = pt.utils.load_imgs('data/images/falling_rocks')
        
        self.master_clock = 0
        self.dt = 0.1
        self.level = 0
        
                
        self.load_level(self.level)
        
    
    def spawn_entities(self):
        self.keys = []
        self.turrets = []
        self.enemies = []
        
        
        keys = self.tilemap.extract(('spawners', (1,)), False, True)
        for key in keys:
            self.keys.append(Key(self, key['pos'], (5, 9)))
            
        turrets = self.tilemap.extract(('spawners', (3,)), False, True)
        for turret in turrets:
            self.turrets.append(Turret(self, turret['pos'], (12, 6)))
            
        moles = self.tilemap.extract(('spawners', (4,)), False, False)
        for mole in moles:
            self.enemies.append(Mole(self, mole['pos'], (6, 5)))
    
    def load_level(self, level):
        self.tilemap.load_map(f'data/maps/map_{level}.json')
        # self.tilemap.load_map('data/maps/test_2.json')
        
        self.transition = -50
        self.keys_collected = 0

        self.door_entered = False

        self.player = Player(self, self.tilemap.extract(('spawners', (0, )), False, False)[0]['pos'], PLAYER_SIZE)
        self.camera.set_target(self.player)
        
        self.falling_rocks = self.tilemap.extract(('decor', (0, 1)), True)
        self.door = self.tilemap.extract(('spawners', (2,)), keep=False)[0]
        
        
        self.spawn_entities()
        
        self.rocks = []
        self.projectiles = []
        self.vfx.reset()
        self.particle_manager.reset()

    def run(self):
        while True:
            
            self.display.fill((8, 20, 30))
            self.ui_display.fill((0, 0, 0, 0))
            
            self.master_clock += 1
            
            if self.transition != 0:
                self.transition =  min(self.transition + 1, 50)
                if (self.transition >= 50) and self.player.dead:
                    self.load_level(self.level)
                elif (self.transition >= 50) and self.door_entered:
                    self.level += 1
                    self.load_level(self.level)
                        
            edges = self.tilemap.get_map_edges()
            clamped = [False, False]
            if self.camera.scroll[0] < edges[0]:
                self.camera.scroll[0] = edges[0]
                clamped[0] = True
            if self.camera.scroll[0] > edges[1] - self.display.get_width():
                self.camera.scroll[0] = edges[1] - self.display.get_width()
                clamped[0] = True
            if self.camera.scroll[1] < edges[2]:
                self.camera.scroll[1] = edges[2]
                clamped[1] = True
            if self.camera.scroll[1] > edges[3] - self.display.get_height():
                self.camera.scroll[1] = edges[3] - self.display.get_height()
                clamped[1] = True
            
            
            door = self.door
            door_img = self.tilemap.tiles[door['type']][door['variant']]
            door_rect = pygame.Rect(door['pos'][0], door['pos'][1], 7, 11)
            if (self.player.rect.collidepoint(door_rect.center)) and not self.transition and (self.keys_collected == len(self.keys)):
                self.transition = max(self.transition, 1)
                self.door_entered = True  
            if self.master_clock // 20 % 4 > 0 and (self.keys_collected == len(self.keys)):
                pt.utils.outline(self.display, door_img, (int(door['pos'][0] - self.camera.pos[0]), int(door['pos'][1] - self.camera.pos[1])))
            self.display.blit(door_img, (int(door['pos'][0] - self.camera.pos[0]), int(door['pos'][1] - self.camera.pos[1])))
            
            self.tilemap.render_visible(self.display, visible_range=self.camera.get_visible_screen, offset=self.camera.pos)
            
            for rock in self.rocks.copy(): # pos, speed, img
                rock[0][1] += rock[1]
                if self.tilemap.tile_collide((rock[0][0] + rock[2].get_width() // 2, rock[0][1] + rock[2].get_height() // 2)):
                    for i in range(4):
                        angle = math.radians(random.uniform(15, 165)) - math.pi
                        speed = 60 + random.random() * 30
                        decay_rate = 300 + random.random() * 40
                        self.vfx.sparks.append(pt.Spark(rock[0],  angle, speed, decay_rate))
                    self.rocks.remove(rock)
                if self.player.rect.collidepoint(rock[0]) and not self.player.hit:
                    self.rocks.remove(rock)
                    self.player.hit = True

                render_pos = (rock[0][0] - self.camera.pos[0], rock[0][1] - self.camera.pos[1])
                pt.utils.outline(self.display, rock[2], render_pos)
                self.display.blit(rock[2], render_pos)
                
            
            for key in self.keys:
                key.update(self.dt) 
                key.render(self.display, offset=self.camera.pos)
                
            for turret in self.turrets:
                turret.update(self.dt) 
                turret.render(self.display, offset=self.camera.pos)

            for torch in self.tilemap.extract(('torches', (0, )), True):
                pt.utils.glow_blit(self.display, loc=(torch['pos'][0] - self.camera.pos[0] - 15 + 5, torch['pos'][1] - self.camera.pos[1] - 15 + 3), radius=15, glow_color=(3, 7, 23))
                pt.utils.glow_blit(self.display, loc=(torch['pos'][0] - self.camera.pos[0] - 27 + 5, torch['pos'][1] - self.camera.pos[1] - 27 + 3), radius=27, glow_color=(3, 7, 23))
                self.particle_manager.particles.append(pt.Particle(self, (torch['pos'][0] + 5, torch['pos'][1] + 3), (4 + random.random() * -8, -4 + random.random() * -8), 'particles', decay_rate=1.7 + random.random(), start_frame=2 + random.random() * 3, glow=(3, 3 + random.randint(1, 3), 8 + random.randint(1, 6)), glow_radius=3 + random.random() * 6))

            for mole in self.enemies:
                mole.update(self.dt)
                mole.render(self.display, offset=self.camera.pos)
            
            self.player.update()
            self.player.render(self.display, offset=(self.camera.float_pos[0] + clamped[0], self.camera.float_pos[1] + clamped[1]))
            
            # pos, angle, speed, timer, 
            for proj in self.projectiles.copy():
                img = self.misc_images['projectile']
                img = pygame.transform.rotate(img, -math.degrees(proj[1]))
                pt.utils.outline(self.display, img, (proj[0][0] - self.camera.pos[0] - img.get_width() // 2, proj[0][1] - self.camera.pos[1] - img.get_height() // 2))
                self.display.blit(img, (proj[0][0] - self.camera.pos[0] - img.get_width() // 2, proj[0][1] - self.camera.pos[1] - img.get_height() // 2))
                
                proj[0][0] += math.cos(proj[1]) * proj[2]
                proj[0][1] += math.sin(proj[1]) * proj[2]
                
                proj[3] += 1
                
                if proj[3] >= 600:
                    self.projectiles.remove(proj)
                if self.player.rect.collidepoint(proj[0]) and not self.player.hit:
                    self.projectiles.remove(proj)
                    self.player.hit = True
                
        
            self.vfx.update(self.dt)
            self.vfx.render(self.display, offset=self.camera.pos)
            
            self.particle_manager.update(self.dt)
            self.particle_manager.render(self.display, self.camera.pos)
            
            self.hud.render(self.ui_display, offset=self.camera.pos)
            
            self.camera.update()
            self.input.update()
                        
            for rock in self.falling_rocks:
                img_size = self.tilemap.tiles[rock['type']][rock['variant']].get_size()
                rock_collide_check = (rock['pos'][0] + random.random() * img_size[0], rock['pos'][1] + img_size[1] - 2)
                if not self.tilemap.tile_collide(rock_collide_check):
                    if random.randint(1, 200) == 1:
                        speed = 0.2 + random.random()
                        img = random.choice(self.fallen_rock_imgs)
                        self.rocks.append([list(rock_collide_check), speed, img])
                        
            
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