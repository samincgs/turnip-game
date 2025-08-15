from .utils import follow_target

class Camera:
    def __init__(self, display_size, lag=20):
        self.display_size = display_size
        self.lag = lag
        
        self.targeted_entity = None
        self.targeted_pos = None
        self.scroll = [0, 0]

    @property
    def pos(self):
        return self.scroll
    
    @property
    def int_pos(self):
        return (int(self.scroll[0]), int(self.scroll[1]))
     
    @property
    def entity_location(self):
        if self.targeted_entity:
            return (self.targeted_entity.pos[0] - self.display_size[0] // 2, self.targeted_entity.pos[1] - self.display_size[1] // 2)
    
    @property
    def target(self):
        if self.targeted_entity:
            target = self.entity_location
        else:
            target = (self.targeted_pos[0] - self.display_size[0] // 2, self.targeted_pos[1] - self.display_size[1] // 2)
        return target
    
    def set_target(self, target, snap=True):
        if hasattr(target, 'center'):
            self.targeted_entity = target
            if snap:
                self.snap_to_target(self.entity_location)
        else:
            self.targeted_pos = target
    
    def snap_to_target(self, pos):
        self.scroll[0] = pos[0]
        self.scroll[1] = pos[1]
    
    def update(self):
        if self.targeted_entity or self.targeted_pos:
            target = self.target
            self.scroll[0] = follow_target(self.scroll[0], target[0], self.lag)
            self.scroll[1] = follow_target(self.scroll[1], target[1], self.lag)
            
        