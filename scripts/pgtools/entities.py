import pygame

class Entity:
    def __init__(self, game, pos, size, e_type):
        self.game = game
        self.pos = list(pos)
        self.size = list(size)
        self.type = e_type
        
        self.active_animation = None
        self.action = None
        
        self.rotation = 0
        self.flip = [False, False]
        self.outline = False
        
        if not self.active_animation:
            self.set_action('idle')
                  
    @property
    def img(self):
        if self.active_animation:
            img = self.active_animation.img
        if any(self.flip):
            img = pygame.transform.flip(img, self.flip[0], self.flip[1])
        if self.rotation:
            img = pygame.transform.rotate(img, self.rotation)
        return img
                
    @property 
    def center(self):
        return [self.pos[0] + self.size[0] // 2, self.pos[1] + self.size[1] // 2]
    
    @property
    def rect(self):
        return pygame.FRect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    @property
    def anim_offset(self):
        offset = (0, 0)
        if self.active_animation:
            offset = self.active_animation.animation['offset']
        return offset
    
    def set_action(self, action, force=False):
        if force or action != self.action:
            self.action = action
            self.active_animation = self.game.animations.new(self.type + '/' + self.action)
    
    def update(self, dt):
        if self.active_animation:
            self.active_animation.update(dt)
        
    def render(self, surf, offset=(0, 0)):
        offset = list(offset)
        offset[0] += self.anim_offset[0]
        offset[1] += self.anim_offset[1]
        surf.blit(self.img, (self.pos[0] - offset[0], self.pos[1] - offset[1]))
        
class PhysicsEntity(Entity):
    def __init__(self, game, pos, size, e_type):
        super().__init__(game, pos, size, e_type)
        self.speed = 0
        self.velocity = [0, 0]
        self.frame_movement = [0, 0]
        self.last_movement = [0, 0]
        self.reset_velocity = True
        
        self.collision_directions = {'up': False, 'down': False, 'right': False, 'left': False}
                
    def move(self, movement, dt):
        self.frame_movement[0] += movement[0] * dt
        self.frame_movement[1] += movement[1] * dt
        self.last_movement = self.frame_movement.copy()
    
    def physics_movement(self, tilemap, movement=(0, 0)):
        self.collision_directions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        self.pos[0] += movement[0]
        tile_rects = tilemap.get_nearby_rects(self.center)
        collision_rects = tilemap.collision_check(self.rect, tile_rects)
        entity_rect = self.rect
        for tile_rect in collision_rects:
            if movement[0] > 0:
                entity_rect.right = tile_rect.left
                self.pos[0] = entity_rect.x
                self.collision_directions['right'] = True
            if movement[0] < 0:
                entity_rect.left = tile_rect.right
                self.pos[0] = entity_rect.x
                self.collision_directions['left'] = True
                
        
        self.pos[1] += movement[1]
        tile_rects = tilemap.get_nearby_rects(self.center)
        collision_rects = tilemap.collision_check(self.rect, tile_rects)
        entity_rect = self.rect   
        
        for tile_rect in collision_rects:
            if movement[1] > 0:
                entity_rect.bottom = tile_rect.top
                self.pos[1] = entity_rect.y
                self.collision_directions['down'] = True
                if self.reset_velocity:
                    self.velocity[1] = 0
            if movement[1] < 0:
                entity_rect.top = tile_rect.bottom
                self.pos[1] = entity_rect.y
                self.collision_directions['up'] = True
                if self.reset_velocity:
                    self.velocity[1] = 0
                    
            
        
            
 
                    
        
        
        
        

            
        
                
        

                
        

        

            
