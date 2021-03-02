# 2D Platform Game 
import pygame, math
from pygame.locals import *

def collision_test_2d(object_0, object_list):
    collision_list = []
    for obj in object_list:
        if obj.colliderect(object_0):
            collision_list.append(obj)
    return collision_list

# `physics_2d` -------------------------------------------------------------------------------#
class physics_2d(object):
    def __init__(self, x, y, width, height):
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.x = x
        self.y = y
    
    def move(self, movement, platforms):
        collision_types = {
            'top': False, 'bottom': False, 'left': False, 'right': False
        }
        
        # holizontal movement
        self.x += movement[0]
        self.rect.x = int(self.x)

        block_hit_list = collision_test_2d(self.rect, platforms)
        for block in block_hit_list:
            if movement[0] > 0:
                self.rect.right = block.left
                collision_types['right'] = True
            elif movement[0] < 0:
                self.rect.left = block.right
                collision_types['left'] = True
            self.x = self.rect.x # ?
        
        # vertical movement
        self.y += movement[1]
        self.rect.y = int(self.y)
        block_hit_list = collision_test_2d(self.rect, platforms)
        for block in block_hit_list:
            if movement[1] > 0:
                self.rect.bottom = block.top
                collision_types['bottom'] = True
            elif movement[1] < 0:
                self.rect.top = block.bottom
                collision_types['top'] = True
            self.y = self.rect.y # ?
        return collision_types

# end of `physics_2d` ------------------------------------------------------------------------#


class animation_data(object):
    def __init__(self, name, path_data, frame_data):
        self.name = name
        self.paths = path_data
        self.frames = frame_data

# `entity_2d` --------------------------------------------------------------------------------#
class entity_2d(object):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.object = physics_2d(self.x, self.y, self.width, self.height)
        self.animation = None
        self.image = None
        self.animation_frame = 0
        self.animation_database = {}
        self.animation_images = {}
        self.flip = False
        self.rotation = 0
        self.action_timer = 0
        self.animation_status = ''
        # self.set_animation('idle')
        self.alpha = None

    def set_pos(self, x, y):
        self.x = x
        self.y = y
        self.object.x = self.x
        self.object.y = self.y
        self.object.rect.x = self.object.x
        self.object.rect.y = self.object.y

    def set_area(self, width, height):
        self.object.width = width
        self.object.height = height
        self.object.rect.width = width
        self.object.rect.height = height

    def move(self, momentum, platforms):
        collisions = self.object.move(momentum, platforms)
        self.x = self.object.x
        self.y = self.object.y
        return collisions

    def set_flip(self, b):
        self.flip = b
    
    def add_animation(self, data: animation_data):
        self.animation_database[data.name] = data
        images = []
        for i in range(len(data.paths)):
            img = pygame.image.load(data.paths[i])
            for _ in range(data.frames[i]):
                images.append(img)
        self.animation_images[data.name] = images.copy()

    def set_animation(self, name, force=False):
        if (self.animation_status == name) and (force == False):
            pass
        else:
            self.animation_status = name
            self.animation = self.animation_database[name]

    def get_entity_angle(self, target):
        x1 = self.x + int(self.width/2)
        y1 = self.y + int(self.height/2)
        x2 = target.x + int(target.width/2)
        y2 = target.y + int(target.height/2)
        angle = math.atan((y2 - y1)/(x2 - x1))
        return angle

    def get_point_angle(self, x, y):
        x1 = self.x + int(self.width/2)
        y1 = self.y + int(self.height/2)
        x2 = x
        y2 = y
        angle =  math.atan2((y2 - y1), (x2 - x1))
        return angle

    def set_image(self, path):
        self.image = pygame.image.load(path)
    
    def display_animation(self, surf, name, scroll=[0, 0]):
        data = self.animation_database[name]
        frames = data.frames
        images = self.animation_images[name]
        if self.animation_frame >= sum(frames):
            self.animation_frame = 0
        image = pygame.transform.flip(images[self.animation_frame], self.flip, False)
        surf.blit(image, (self.x - scroll[0], self.y - scroll[1]))
        self.animation_frame += 1

    def change_action():
        pass
    
    def display_image(self, surf: pygame.Surface):
        image = pygame.trasform.flip(self.image)
        surf.blit(image, (self.x, self.y))

# end of `entity_2d` -------------------------------------------------------------------------#

# --------------------------------------------------------------------------------------------#

def y_inertia(object_momentum, gravity_momentum, limit):
    momentum = object_momentum - gravity_momentum
    if momentum > limit:
        momentum = limit
    return momentum

def x_inertia(object_momentum, momentum, limit):
    momentum = object_momentum + momentum
    if momentum > 0 and momentum > limit:
        momentum = limit
    if momentum < 0 and momentum < limit:
        momentum = limit
    return momentum

def calc_scroll(center, scroll, display_size, delay):
    scroll[0] += ((center[0] - scroll[0]) - display_size[0]/2)/delay
    scroll[1] += ((center[1] - scroll[1]) - display_size[1]/2)/delay



class camera_2d(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))

    def display(self, screen, size, loc=(0, 0)):
        surf = pygame.transform.scale(self.surface, size)
        screen.blit(surf, loc)

# tile map -----------------------------------------------------------------------------------#
class tile_map_2d(object):
    def __init__(self, tile_size: int):
        self.tile_index = {}
        self.key_map = []
        self.rects = [] # reset every frame
        self.tile_size = tile_size

    # def generate_map_key(x, y):
    #    return str(x) + "," + str(y)

    def add_tile(self, key, tile):
        self.tile_index[key] = tile
        pass

    def set_tile(self, key, x, y):
        self.key_map[y][x] = key

    def key_from_txt(self, path):
        with open(path, 'r') as f:
            data = f.read()
            f.close()
            data = data.split('\n')
            for row in data:
                self.key_map.append(list(row))

    def map_from_json(self, path):
        pass

    def render_tile(self, surf, x: int, y :int, scroll):
        # if key is valid
        if self.key_map[y][x] in self.tile_index:
            tile = self.tile_index[self.key_map[y][x]] # type(tile) == tile_object_2d
            location = [0, 0]
            location[0] = x*self.tile_size - scroll[0]
            location[1] = y*self.tile_size - scroll[1]
            surf.blit(tile.image, (location[0], location[1]))
            if tile.is_rect:
                self.rects.append(pygame.Rect(
                    x*self.tile_size, y*self.tile_size, self.tile_size, self.tile_size
                ))
        else:
            pass

    def render_map(self, surf, scroll):
        self.rects = []
        for y in range(len(self.key_map)):
            for x in range(len(self.key_map[y])):
                self.render_tile(surf, x, y, scroll)


class tile_object_2d(object):
    def __init__(self, path, is_rect):
        self.image = pygame.image.load(path)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.is_rect = is_rect
    
# particles ----------------------------------------------------------------------------------#
# * location
# * move around
# * changes over time
# * disappear

class simple_particle(object):
    def __init__(self, x, y, momentum, duration, default_radius):
        self.x = x
        self.y = y
        self.radius = default_radius
        self.momentum = momentum
        self.disappear_timer = duration
        self.disappear_time = duration
        self.gravity = 0.0

    def move(self, gravity=0):
        self.gravity = gravity
        self.x += self.momentum[0]
        self.y += self.momentum[1] + self.gravity
        self.momentum[1] += self.gravity
    
    def move_with_momentum(self, momentum):
        self.momentum = momentum
        self.move(self.gravity)
   
    def render(self, screen, color, scroll):
        self.disappear_timer -= 1
        self.radius *= round(self.disappear_timer/self.disappear_time)
        if self.radius < 1:
            self.disappear_timer = 0
        pygame.draw.circle(
            screen, 
            color, 
            (int(self.x - scroll[0]), int(self.y - scroll[1])), 
            self.radius
        )

