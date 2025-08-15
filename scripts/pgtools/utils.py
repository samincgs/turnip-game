import pygame
import os
import json

# load pygame image
def load_img(path, colorkey=(0, 0, 0), alpha=False):
    img = pygame.image.load(path).convert_alpha() if alpha else pygame.image.load(path).convert()
    if colorkey:
        img.set_colorkey(colorkey)
    return img

# load a directory of imgs in a list
def load_imgs(path, colorkey=(0, 0, 0), alpha=False):
    imgs = []
    for file in sorted(os.listdir(path)):
        img = load_img(path + '/' + file, colorkey=colorkey, alpha=alpha)
        imgs.append(img)
    return imgs

# load a directory of images into a dictionary
def load_dir(path, colorkey=(0, 0, 0), alpha=False):
    imgs = {}
    for file in sorted(os.listdir(path)):
        name = file.split('.')[0]
        img = load_img(path + '/' + file, colorkey=colorkey, alpha=alpha)
        imgs[name] = img
    return imgs

# load multiple directories into a dict with lists of images
def load_dir_list(path, colorkey=(0, 0, 0), alpha=False):
    image_dir = {}
    for folder in sorted(os.listdir(path)):
        image_dir[folder] = []
        for img in os.listdir(path + '/' + folder):
            image_dir[folder].append(load_img(os.path.join(path, folder, img), colorkey, alpha))                                       
    return image_dir

# load all sound files from a directory into a dict
def load_sounds(path):
    sounds = {}
    for file in sorted(os.listdir(path)):
        name = file.split('.')[0]
        sound = pygame.mixer.Sound(path + '/' + file)
        sounds[name] = sound
    return sounds

# load a json file and return its data
def load_json(path):
    f = open(path)
    map_data = json.load(fp=f)
    f.close()
    return map_data

# open a file and save data into the file
def save_json(path, data):
    f = open(path, 'w')
    json.dump(data, fp=f)
    f.close()

# load a text file into a 2D list of numbers (can be string or int)
def load_map_txt(path, ints=False):
    map = []
    data = read_file(path)
    data = data.split('\n')
    for row in data:
        if not ints:
            map.append(row.split())
        else:
           map.append([int(num) for num in row.split()])
    return map

# read a text file
def read_file(path):
    f = open(path, 'r')
    data = f.read()
    f.close()
    return data

# create a smaller subsurface of a bigger surface
def clip(surf, loc, size):
    main_surf = surf.copy()
    clipped_rect = pygame.Rect(loc[0], loc[1], size[0], size[1])
    main_surf.set_clip(clipped_rect)
    img = main_surf.subsurface(main_surf.get_clip())
    return img.copy()

# do a color swap, between an old and new color
def palette_swap(img, old_color, new_color):
    handle_img = img.copy()
    handle_img.fill(new_color)
    img.set_colorkey(old_color)
    handle_img.blit(img, (0, 0))
    return handle_img 

def outline(surf, img, loc, color=(255, 255, 255)):
    mask_img = pygame.mask.from_surface(img)
    mask_img = mask_img.to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))
    for offset in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
        surf.blit(mask_img, (loc[0] + offset[0], loc[1] + offset[1]))
        
def glow_blit(surf, loc, radius, glow_color):
        glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        glow_surf.set_colorkey((0, 0, 0))
        pygame.draw.circle(glow_surf, glow_color, (radius, radius), radius)
        surf.blit(glow_surf, loc, special_flags=pygame.BLEND_RGB_ADD)

def normalize(vel, amt, target=0):
    if vel > target:
        return max(vel - amt, target)
    elif vel < target:
        return min(vel + amt, target)
    return target

def follow_target(val, target, lag):
    val += (target - val) / lag
    return val

def load_spritesheets(path):
        """Loads all spritesheets in a directory and extracts sprites."""
        
        CYAN = (0, 255, 255)
        MAGENTA = (255, 0, 255)
        
        spritesheet_dict = {}
        tileset_config = {}
        
        for img_file in os.listdir(path):
            if img_file.endswith('.png'): 
                tile_name = img_file.split('.')[0]  
                spritesheet_dict[tile_name] = []
                
                spritesheet = load_img(os.path.join(path, img_file))
                
                y = 1
                start_x = 1
                
                
                while y < spritesheet.get_height():
                    tile_end = None
                    end_x = None
                    
                    for y2 in range(y, spritesheet.get_height()):
                        if spritesheet.get_at((start_x, y2))[:3] in {MAGENTA, CYAN}: # MAGENT, CYAN
                            tile_end = y2 - 1
                            break
                    
                    for x2 in range(start_x, spritesheet.get_width()):
                        if spritesheet.get_at((x2, y))[:3] in {MAGENTA, CYAN}: # MAGENTA or CYAN
                            end_x = x2 - 1
                            break
                        
                    
                    if tile_end is not None and end_x is not None:
                        width, height = end_x - start_x + 1, tile_end - y + 1
                        img = clip(spritesheet, (start_x, y), (width, height))

                        spritesheet_dict[tile_name].append(img)

                        y = tile_end + 3 

                    else:
                        y += 1
                        
                if spritesheet.get_at((0, 0)) == CYAN:
                    if tile_name + '.json' not in os.listdir(path):
                        tile_variants = len(spritesheet_dict[tile_name])
                        data = {'tile_offsets': {}}
                        for i in range(tile_variants):
                            data['tile_offsets'][str(i)] = [0, 0]
                        save_json(path + tile_name + '.json', data)
        
        for img_file in os.listdir(path):
            if img_file.endswith('.json') and img_file.split('.')[0] in spritesheet_dict:
                 tileset_config[img_file.split('.')[0]] = load_json(path + img_file)
                
                
                                
        return spritesheet_dict