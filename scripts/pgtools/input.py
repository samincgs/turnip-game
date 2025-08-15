import pygame
import sys

RENDER_SCALE = 4
INPUT_MAP = {
    'mouse': {
        'click': 1
        },
    'keyboard': {
        'left': 97,
        'right': 100,
        'jump': 32,         
    }
     
}


class InputState:
    def __init__(self, input_type, id):
        self.type = input_type
        self.id = id
        
        self.held = False
        self.pressed = False
        self.clicked = False
              
    def press(self):
        self.held = True
        if self.type == 'mouse':
            self.clicked = True
        if self.type == 'keyboard':
            self.pressed = True
        
    def release(self):
        self.pressed = False
        self.held = False
        self.clicked = False
        
    def reset(self):
        self.pressed = False
        self.clicked = False
    
class Input:
    def __init__(self):
        self.keyboard = {key: InputState('keyboard', INPUT_MAP['keyboard'][key]) for key in INPUT_MAP['keyboard']}
        self.mouse = {btn: InputState('mouse', INPUT_MAP['mouse'][btn]) for btn in INPUT_MAP['mouse']}
        self.mpos = (0, 0)
    
    def pressed(self, key):
        return self.keyboard[key].pressed
    
    def holding(self, key):
        return self.keyboard[key].held
    
    def clicking(self, btn):
        return self.mouse[btn].clicked
    
    def update(self):
        all_triggers = {*self.keyboard, *self.mouse}
        for trigger in all_triggers:
            if trigger in self.keyboard:
                self.keyboard[trigger].reset()
            else:
                self.mouse[trigger].reset()
                
        self.mpos = pygame.mouse.get_pos()
        self.mpos = (self.mpos[0] // RENDER_SCALE, self.mpos[1] // RENDER_SCALE)
                   
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in self.mouse:
                    if event.button == self.mouse[btn].id:
                        self.mouse[btn].press()
            if event.type == pygame.MOUSEBUTTONUP:
                for btn in self.mouse:
                    if event.button == self.mouse[btn].id:
                        self.mouse[btn].release()
            if event.type == pygame.KEYDOWN:
                # print(event.key)
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                for key in self.keyboard:
                    if event.key == self.keyboard[key].id:
                        self.keyboard[key].press() 
            if event.type == pygame.KEYUP:  
                for key in self.keyboard:
                    if event.key == self.keyboard[key].id:
                        self.keyboard[key].release()
                        
                        
                
        
        