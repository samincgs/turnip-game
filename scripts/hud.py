import scripts.pgtools as pt

class HUD:
    def __init__(self, game):
        self.game = game
        
        self.tutorial = {'space': False, 'd': False, 'a': False}
        self.icons = pt.utils.load_dir('data/images/icons')
        
             
    def render(self, surf, offset=(0, 0)):
        for btn in self.tutorial:
            if not self.tutorial[btn]:
                btn_img = self.icons[btn]
                if btn == 'space':
                    surf.blit(btn_img, (self.game.player.center[0] - offset[0] - btn_img.get_width() // 2 - 1, self.game.player.pos[1] - offset[1] - 9 - btn_img.get_height()))
                if btn == 'd':
                    surf.blit(btn_img, (self.game.player.center[0] - offset[0] - btn_img.get_width() // 2 + 8, self.game.player.pos[1] - offset[1] - btn_img.get_height()))
                if btn == 'a':
                    btn_img = self.icons[btn] if self.game.master_clock % 60 < 30 else self.icons[btn + '_pressed']
                    surf.blit(btn_img, (self.game.player.center[0] - offset[0] - btn_img.get_width() // 2 - 9, self.game.player.pos[1] - offset[1] - btn_img.get_height()))