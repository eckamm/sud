"""
z2.py with Sprites
"""
import sys, random
import pygame
from pygame.locals import *
from pygame.color import *
import pygame.sprite
import pygame.image
import pygame.transform
import pymunk

from itertools import cycle


SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
FRICTION = 1.0


def add_walls(space):
    body = pymunk.Body()
    body.position = (0, 0)
    walls = []
    walls.append(pymunk.Segment(body, (10, 10), (10, 590), 10))
    walls.append(pymunk.Segment(body, (590, 10), (590, 590), 10))
    walls.append(pymunk.Segment(body, (10, 10), (590, 10), 10))
    walls.append(pymunk.Segment(body, (10, 590), (590, 590), 10))
    for wall in walls:
        wall.friction = FRICTION
        space.add(wall)
    return walls


def draw_walls(screen, walls):
    for wall in walls:
        body = wall.body
        pv1 = body.position + wall.a.rotated(body.angle) # 1
        pv2 = body.position + wall.b.rotated(body.angle)
        p1 = to_pygame(pv1) # 2
        p2 = to_pygame(pv2)
        pygame.draw.lines(screen, THECOLORS["red"], False, [p1,p2])




def add_static_L(space):
    body = pymunk.Body() # 1
    body.position = (280, 300)
    l1 = pymunk.Segment(body, (-150, 0), (255, 0), 5) # 2
    l2 = pymunk.Segment(body, (-150, 0), (-150, 50), 5)

    space.add(l1, l2) # 3
    return l1,l2


def draw_lines(screen, lines):
    for line in lines:
        body = line.body
        pv1 = body.position + line.a.rotated(body.angle) # 1
        pv2 = body.position + line.b.rotated(body.angle)
        p1 = to_pygame(pv1) # 2
        p2 = to_pygame(pv2)
        pygame.draw.lines(screen, THECOLORS["lightgray"], False, [p1,p2])


def to_pygame(p):
    """Small hack to convert pymunk to pygame coordinates"""
    return int(p.x), int(-p.y+600)


def add_ball(space, img):
    mass = 1
    radius = 30
    inertia = pymunk.moment_for_circle(mass, 0, radius) # 1
    body = pymunk.Body(mass, inertia) # 2
    x = random.randint(120,380)
    body.position = x, 550 # 3
    shape = pymunk.Circle(body, radius) # 4
    shape.friction = FRICTION
    space.add(body, shape) # 5

    sprite = MySprite(img, shape)

    return shape, sprite


class MySprite(pygame.sprite.Sprite):
    def __init__(self, img, shape):
        pygame.sprite.Sprite.__init__(self)
        self.o_image = img
        self.shape = shape  # a pymunk.Shape

    def update(self):
        x = self.shape.body.position.x
        y = self.shape.body.position.y

        self.image = pygame.transform.rotate(self.o_image, self.shape.body.angle)

        r = self.image.get_rect()
        r.center = (x, SCREEN_HEIGHT-y)
        self.rect = r

        print self.shape.body.angle



def draw_ball(screen, ball):
    p = int(ball.body.position.x), 600-int(ball.body.position.y)
    pygame.draw.circle(screen, THECOLORS["blue"], p, int(ball.radius), 2)


def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("You call yourself a game?")


    image_file = "kewlapple_64x64.png"
    img = pygame.image.load(image_file)
    grp = pygame.sprite.Group()


    clock = pygame.time.Clock()
    running = True

    space = pymunk.Space()
    space.gravity = (0.0, -300.0)
    space.gravity = (300.0, -300.0)

#   lines = add_static_L(space)
    walls = add_walls(space)
    balls = []

    gravities = cycle([
        (0.0, -300.0),
#       (0.0, 0.0),
        (300.0, 0.0),
#       (0.0, 0.0),
        (0.0, 300.0),
#       (0.0, 0.0),
        (-300.0, 0.0),
#       (0.0, 0.0),
    ])


    ticks_to_next_gravity_change = 50
    ticks_to_next_ball = 15
    debug = 0
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False
            elif event.type == KEYDOWN and event.key == K_d:
                debug = (debug+1) % 2                

        if len(balls) < 50:
            ticks_to_next_ball -= 1
            if ticks_to_next_ball <= 0:
                ticks_to_next_ball = 25
                ball_shape, ball_sprite = add_ball(space, img)
                grp.add(ball_sprite)
                balls.append(ball_shape)

        ticks_to_next_gravity_change -= 1
        if ticks_to_next_gravity_change <= 0:
            ticks_to_next_gravity_change = 50
            space.gravity = gravities.next()

        screen.fill(THECOLORS["white"])

        if debug:
            for ball in balls:
                draw_ball(screen, ball)

#       draw_lines(screen, lines)
        draw_walls(screen, walls)

        grp.update()
        grp.draw(screen)

        space.step(1/50.0)

        pygame.display.flip()
        clock.tick(50)

if __name__ == '__main__':
    sys.exit(main())

