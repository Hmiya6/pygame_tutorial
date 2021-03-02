import pygame, sys, random, math, time
from pygame.locals import *
from pygame.constants import (
    QUIT, KEYDOWN, K_w, K_a, K_s, K_d, K_q, K_e, K_f
)
from pygame import (
    display, event, key, time
)
import engine as e

clock = pygame.time.Clock()
# dt = time.time()
pygame.init()

WINDOW_SIZE = (900, 600)
CAMERA_SIZE = (WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/2)
TILE_SIZE = 16
FRAME_RATE = 60
true_scroll = []
scroll = []

class player_character(object):
    JUMP = 2
    def __init__(self, x, y, width, height):
        self.entity = e.entity_2d(x, y, width, height)
        self.momentum = [0, 0]
        self.collisions = {'top': False, 'bottom': False, 'left': False, 'right': False}
        self.air_timer = 0.0
        self.jump_counter = 0
        self.moving_right = False
        self.moving_left = False
        
        # add idle animation
        idle_animation_paths = [
            'assets/player_animations/idle/idle_' + str(i) + '.png' for i in range(0, 2)
        ]
        self.entity.add_animation(e.animation_data('idle', idle_animation_paths, [16, 80]))
        # add run animation
        run_animation_paths = [
            'assets/player_animations/run/run_' + str(i) + '.png' for i in range(0, 3)
        ]
        self.entity.add_animation(e.animation_data('run', run_animation_paths, [12, 12, 12]))
        
    
    def move(self, platforms):
        self.calc_momentum()
        self.gravity_process()
        if self.air_timer == 10:
            self.jump_counter = self.JUMP - 1
        self.collisions = self.entity.move(self.momentum, platforms)
        if self.collisions['bottom']:
            self.momentum[1] = 0
            self.air_timer = 0.0
            self.jump_counter = self.JUMP
        else:
            self.air_timer += 1
        if self.collisions['top']:
            self.momentum[1] = 0


    def calc_momentum(self):
        if self.moving_right:
            self.momentum[0] += 0.2
            if self.momentum[0] > 2:
                self.momentum[0] = 2
        if self.moving_left:
            self.momentum[0] -= 0.2
            if self.momentum[0] < -2:
                self.momentum[0] = -2

    def key_event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_a:
                self.moving_left = True
                self.entity.flip = True
            if event.key == K_d:
                self.moving_right = True
                self.entity.flip = False
            if event.key == K_SPACE or event.key == K_w:
                if self.air_timer < 8 or self.jump_counter > 0:
                    self.jump()
                    self.jump_counter -= 1
        if event.type == KEYUP:
            if event.key == K_a:
                self.moving_left = False
                self.momentum[0] = 0
            if event.key == K_d:
                self.moving_right = False
                self.momentum[0] = 0

    def jump(self):
        self.momentum[1] = -5

    def render_animation(self, surf, scroll):
        if self.moving_right or self.moving_left:
            self.entity.display_animation(surf, 'run', scroll)
        else :
            self.entity.display_animation(surf, 'idle', scroll)

    def gravity_process(self):
        if not self.collisions['bottom']:
            self.momentum[1] += 0.2
            if self.momentum[1] > 3:
                self.momentum[1] = 3

class enemy_character(object):
    def __init__(self, x, y):
        self.entity = e.entity_2d(x, y, 14, 7)
        self.base_speed = 1
        self.momentum = [0, 0]
        self.collisions = {'top': False, 'bottom': False, 'right': False, 'left': False}
        self.collision_bool = False
        self.player_collision = False
        move_animation_paths = [
            'assets/enemy_animtions/move/enemy_' + str(i) + '.png' for i in range(4)
        ]
        self.entity.add_animation(e.animation_data('move', move_animation_paths, [8, 8, 8, 8]))
    
    def move(self, target_location, platforms):
        self.momentum = self.calc_momentum(self.base_speed, target_location)
        cols = self.entity.move(self.momentum, platforms)
        self.collision_bool = cols['top'] or cols['bottom'] or cols['right'] or cols['left']
        # if self.collision_bool:
        #     self.explode()
        
    def calc_momentum(self, base_speed, target):
        angle = self.entity.get_point_angle(target[0], target[1])
        return [base_speed*math.cos(angle), base_speed*math.sin(angle)]

    def process(self, target_location, platforms, surf, scroll):
        self.move(target_location, platforms)
        self.render_animation(surf, scroll)

    def render_animation(self, surf, scroll):
        self.entity.display_animation(surf, 'move', scroll)
    """
    def explode(self):
        self.explosion_particles = []
        for _ in range(100):
            angle = random.random()*math.pi*2
            speed = 2
            momentum = (speed*math.cos(angle), speed*math.sin(angle))
            particle = e.simple_particle(self.entity.x, self.entity.y, momentum, random.randint(10, 80), 3)
            self.explosion_particles.append(particle)
        pass
    def render_explosion(self, screen, scroll):
        if len(self.explosion_particles) <= 0:
            return
        for particle in self.explosion_particles:
            particle.render(screen, (255, 255, 255), scroll)
            if particle.disappear_timer < 0:
                self.explosion_particles.remove(particle)

class explosion_particle(object):
    def __init__(self, x, y, momentum, duration, default_radius):
        self.particle = e.simple_particle(x, y, momentum, duration, default_radius)
    
    def render(self, screen, color, scroll):
        self.particle.render(screen, color, scroll)
"""
class Explosion(object):
    def __init__(self, x, y, num, speed, gravity=0):
        self.particles = []
        self.is_end = False
        self.gravity = gravity
        for _ in range(num):
            angle = random.random()*math.pi*2
            momentum = [math.cos(angle)*speed, math.sin(angle)*speed]
            duration = random.randint(100, 1000)
            particle = e.simple_particle(x, y, momentum, duration, 2)
            self.particles.append(particle)
    
    def render(self, screen, scroll):
        if len(self.particles) > 0:
            for particle in self.particles:
                particle.move(self.gravity)
                particle.render(screen, (255, 255, 255), scroll)
                if particle.disappear_timer <= 0:
                    self.particles.remove(particle)
        else:
            self.is_end = True


class stage(e.tile_map_2d):
    def __init__(self):
        super().__init__(TILE_SIZE)
        self.add_tile('1', e.tile_object_2d('assets/rock.png', True))
        self.add_tile('2', e.tile_object_2d('assets/grass_rock.png', True))
        self.add_tile('3', e.tile_object_2d('assets/grass.png', False))

class background_ruin(object):
    def __init__(self, location, delay):
        self.image = pygame.image.load('assets/ruins.png').convert()
        self.image.set_colorkey((0,0,0))
        self.size = (self.image.get_width(), self.image.get_height())
        self.image = pygame.transform.scale(self.image, (self.size[0]*4, self.size[1]*4))
        self.size = (self.image.get_width(), self.image.get_height())
        self.delay = delay
        self.location = location

    def render(self, surf, scroll=(0, 0)):
        surf.blit(self.image, ((self.location[0] - scroll[0])/self.delay, (self.location[1] - scroll[1])/self.delay))

def lighting_surface(radius, color):
    surf = pygame.Surface((radius*2, radius*2))
    pygame.draw.circle(surf, color, (radius, radius), radius)
    surf.set_colorkey((0,0,0))
    return surf

def main() :
    pygame.init()
    pygame.display.set_caption('2D Scroll Game v0.0.2')
    screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
    camera = e.camera_2d(CAMERA_SIZE[0], CAMERA_SIZE[1])
    display = camera.surface
    player_size = (6, 14)
    player = player_character(50, 50, player_size[0], player_size[1])
    true_scroll = [0.0, 0.0]
    scroll = [0, 0]
    ruin = background_ruin((0, 240), 4)
    tile_map = stage()
    tile_map.key_from_txt('map.txt')
    enemys = []
    for _ in range(5):
        rand_x = random.randint(0, 20*TILE_SIZE)
        enemy = enemy_character(rand_x, 1*TILE_SIZE)
        enemys.append(enemy)
    explosions = []
    # particle experiment --------------------------------------------------------------------#
    particles = []
    # end ------------------------------------------------------------------------------------#
    # last_time = time.tiem()

    
    # ----------------------------------------------------------------------------------------#
    while True:
        # dt = time.time() - last_time
        # dt *= 60
        # last_time = time.time()

        # background
        display.fill((0, 0, 0))
        # display.fill((60, 90, 200))
        
        scroll_delay = 10
        true_scroll[0] += ((player.entity.object.x - true_scroll[0]) - CAMERA_SIZE[0]/2)/scroll_delay
        true_scroll[1] += ((player.entity.object.y - true_scroll[1]) - CAMERA_SIZE[1]/2)/scroll_delay
        scroll = true_scroll.copy()
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])
        
        # render
        ruin.render(display, scroll)
        player.render_animation(display, scroll)
        for enemy in enemys: 
            enemy.render_animation(display, scroll)
            if enemy.collision_bool:
                explosion_ins = Explosion(enemy.entity.x, enemy.entity.y, 16, 2, 0.1)
                explosions.append(explosion_ins)
                enemys.remove(enemy)
        for explosion in explosions:
            explosion.render(display, scroll)
            if explosion.is_end:
                explosions.remove(explosion)

        tile_map.render_map(display, scroll)
        map_rects = tile_map.rects
        
        # particle experiment ----------------------------------------------------------------#
        angle = random.random()*math.pi/2 - math.pi*3/4
        speed = 1
        momentum = [speed*math.cos(angle), speed*math.sin(angle)]
        particles.append(e.simple_particle(100, -200, momentum,random.randint(10, 500), 2))
        print(len(particles), end='\r')
        for particle in particles:
            particle.move(0.04)
            # particle
            # particle.render(display, (240, 120, 80), scroll)
            radius = 2 * 12
            light_colors = [(5, 5, 5), (10, 10, 10), (20, 20, 20)]
            display.blit(lighting_surface(radius, light_colors[random.randint(0, 2)]), ((particle.x - scroll[0] - radius), (particle.y - scroll[1] - radius)), special_flags=BLEND_RGB_ADD)
            particle.render(display, (255, 255, 255), scroll)
            if particle.disappear_timer < 1:
                particles.remove(particle)
        # end --------------------------------------------------------------------------------#
        

        player.move(map_rects)
        player_location = (player.entity.x, player.entity.y)
        for enemy in enemys: enemy.move(player_location, map_rects)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            player.key_event(event)
        
        # player.render_animation(display, scroll)

        camera.display(screen, WINDOW_SIZE)
        pygame.display.update()
        clock.tick(FRAME_RATE)



if __name__ == '__main__':
    main()

