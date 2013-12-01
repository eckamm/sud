"""
Schnauzer's Unindustrialized Diffusion
a game idea

only one known solution per level
take away the element that led to the solution


    * one ball; walls; one blob
    * two balls; walls; one blob
    * one ball; no walls; one blob
    * two balls; no walls; two blobs
    * three balls; walls; two blobs

    
elements:
    * number of balls
    * number of blobs
    * size of blobs
    * walls / no walls
    * floor / no floor
    * time limit
    * points for time left
    * ball size
    * falling obstacles
    * gravity direction


gravity rotates around; get ball into center
    * location of goal zone
    * shifting gravity

scoring:
    * countdown timer; more time left gives more points
    * bonus; finish soon enough and more balls appear

"""
import sys, random
import os
import glob
from itertools import cycle
import json

from poc1_header import *

#import pygame
#from pygame.locals import *
#from pygame.color import *

import pymunk
from pymunk.vec2d import Vec2d
import pymunk.pygame_util

from blob import Blob
from blob2 import Blob2 as Blob
from blob3 import Blob3 as Blob
from zzz import ZZZ

from goal import Goal


def to_pygame(p):
    """Small hack to convert pymunk to pygame coordinates"""
    return int(p.x), int(-p.y+SCREEN_HEIGHT)


def from_pygame(p):
    """Small hack to convert pygame to pymunk coordinates"""
    return Vec2d(p[0], SCREEN_HEIGHT-p[1])



class Walls:
    def __init__(self, space, color="blue"):
        self.color = THECOLORS[color]
        body = pymunk.Body()
        body.position = (0, 0)
        walls = []
        x = WALLMARGIN
        a = MARGIN
        b = SCREEN_WIDTH - MARGIN
        walls.append(pymunk.Segment(body, (a, a), (a, b), x))
        walls.append(pymunk.Segment(body, (b, a), (b, b), x))
        walls.append(pymunk.Segment(body, (a, a), (b, a), x))
        walls.append(pymunk.Segment(body, (a, b), (b, b), x))
        print ((a, a), (a, b), x)
        print ((b, a), (b, b), x)
        print ((a, a), (b, a), x)
        print ((a, b), (b, b), x)
        for wall in walls:
            wall.friction = FRICTION
            wall.elasticity = ELASTICITYW
            wall.collision_type = CT_WALL
            space.add(wall)
        self.walls = walls

    def draw(self, surface):
        for wall in self.walls:
            body = wall.body
            pv1 = body.position + wall.a.rotated(body.angle) # 1
            pv2 = body.position + wall.b.rotated(body.angle)
            p1 = to_pygame(pv1) # 2
            p2 = to_pygame(pv2)
            if Globals.gfxdraw:
                pygame.gfxdraw.aaline(surface, p1[0], p1[1], p2[0], p2[1], self.color)
            else:
                pygame.draw.lines(surface, self.color, False, [p1,p2])


class Walls:
    def __init__(self, space, segs):
        self.segs = segs

        body = pymunk.Body()
        body.position = (0, 0)

        self.segs = []

        for pargs, kwargs in segs:
            pargs[0] = tuple(pargs[0])
            pargs[1] = tuple(pargs[1])
            seg = pymunk.Segment(body, *pargs)
            seg.friction = FRICTION
            seg.elasticity = ELASTICITYW
            seg.collision_type = CT_WALL
            seg.color = THECOLORS[kwargs.get("color", "blue")]
            self.segs.append(seg)
            space.add(seg)

    def draw(self, surface):
        for seg in self.segs:
            body = seg.body
            pv1 = body.position + seg.a.rotated(body.angle) # 1
            pv2 = body.position + seg.b.rotated(body.angle)
            p1 = to_pygame(pv1) # 2
            p2 = to_pygame(pv2)
            pygame.draw.lines(surface, seg.color, False, [p1,p2])




'''
class Goal:
    def __init__(self, space, coord0, coord1, coord2, color="blue"):
        self.color = THECOLORS[color]
        body = pymunk.Body()
        body.position = Vec2d(*coord0)
        self.seg = pymunk.Segment(body, Vec2d(*coord1), Vec2d(*coord2), 0)
        self.seg.friction = FRICTION
        self.seg.collision_type = CT_GOAL
        space.add(self.seg)

    def draw(self, surface):
        body = self.seg.body
        pv1 = body.position + self.seg.a.rotated(body.angle) # 1
        pv2 = body.position + self.seg.b.rotated(body.angle)
        p1 = to_pygame(pv1) # 2
        p2 = to_pygame(pv2)
        #pygame.draw.lines(surface, THECOLORS["yellow"], False, [p1,p2])

        m = RADIUS*2
        a, b = p1
        c, d = p2
        pygame.draw.lines(surface, self.color, False, [(a-m, b-m), (c+m, d-m)]) # top
        pygame.draw.lines(surface, self.color, False, [(a-m, b+m), (c+m, d+m)]) # bottom

        pygame.draw.lines(surface, self.color, False, [(a-m, b-m), (a-m, b+m)]) # left
        pygame.draw.lines(surface, self.color, False, [(c+m, d-m), (c+m, d+m)]) # right
'''


class Ball:
    def __init__(self, img, space, coord, max_data=15, radius=20, color="skyblue"):
        self.color = THECOLORS[color]
        self.img = img
        self.space = space
        #self.data = [] # list of tuples of (coord, shape)
        #self.max_data = max_data
        self.radius = radius
        self._add(Vec2d(*coord))

    def _add(self, coord):
        mass = 1
        inertia = pymunk.moment_for_circle(mass, 0, self.radius) # 1
        body = pymunk.Body(mass, inertia) # 2
        body.position = coord
        shape = pymunk.Circle(body, self.radius) # 4
        shape.friction = FRICTION
        shape.elasticity = ELASTICITYT
        self.space.add(body, shape) # 5
        self.shape = shape
        self.shape.collision_type = CT_BALL
        self.shape.ball = self

    def draw(self, surface):
        coord = self.shape.body.position
        p = ( int(coord[0]), SCREEN_HEIGHT-int(coord[1]) )
        if Globals.gfxdraw:
            pygame.gfxdraw.aacircle(surface, p[0], p[1], self.radius, self.color)
        else:
            pygame.draw.circle(surface, self.color, p, self.radius, 2)

    def freeze(self):
        """
        replace the body with a static body
        """
        coord = self.shape.body.position
        self.space.remove(self.shape.body)
        self.space.remove(self.shape)

        body = pymunk.Body() # static
        body.position = coord
        shape = pymunk.Circle(body, self.radius)
        shape.friction = FRICTION
        shape.elasticity = ELASTICITYT
        self.space.add(shape)

        self.done = 1 # signal that this ball is finished

        scorer.update(100, 0.0)



def collision_begin(space, arbiter, *args, **kwargs):
    """
    a CT_BALL colliding with a CT_WALL makes calls ball.freeze()
    """
    ball_shape = arbiter.shapes[0]
    ball_shape.ball.freeze()
    return True


class Level:
    def __init__(self, space, walls, goals, blobs, balls, zzzs):
        self.space = space
        self.walls = walls
        self.goals = goals
        self.blobs = blobs
        self.blob_idx = 0
        self.balls = balls
        self.zzzs = zzzs

    def draw(self, surface):
        for wall in self.walls:
            wall.draw(surface)
        for goal in self.goals:
            goal.draw(surface)
        for blob in self.blobs:
            blob.draw(surface)
        for ball in self.balls:
            ball.draw(surface)
        for zzz in self.zzzs:
            zzz.draw(surface)

    def update(self):
        self.space.step(1/float(TICK))
        for blob in self.blobs:
            blob.update()
        for ball in self.balls:
            if ball.shape.body.position.x > 1000:
                return True
            elif ball.shape.body.position.x < -1000:
                return True
            elif ball.shape.body.position.y > 1000:
                return True
            elif ball.shape.body.position.y < -1000:
                return True
        return False
    
    

# goals: def __init__(self, space, coord0, coord1, coord2):
# blobs: def __init__(self, space, max_data=15, radius=20):
# balls: def __init__(self, img, space, coord, max_data=15, radius=20):

SAMPLE_LEVEL = """
{
    "space": {
        "gravity": [0, -300]
    },
    "goals": [
        [ [[250, 100], [0, 0], [100, 0]], {} ]
    ],
    "blobs": [
        [ [], {"max_data": 50} ],
        [ [], {"max_data": 20} ]
    ],
    "balls": [
        [ [[200, 400]], {"max_data":15, "radius":20} ]
    ]
}
"""

def make_level_from_json(jdat, round):

    with open("walls.json") as fp:
        wall_defns = json.load(fp)

    space = pymunk.Space()
    space.gravity = Vec2d(*jdat["space"]["gravity"])
    space.add_collision_handler(CT_BALL, CT_GOAL, begin=collision_begin)
    space.add_collision_handler(CT_ZZZ, CT_BLOB, begin=lambda a,b:False)
    space.add_collision_handler(CT_BLOB, CT_BLOB, begin=lambda a,b:False)

    #
    wall_refs = jdat.get("wall-refs", "border")
    walls = []
    for wall_ref in wall_refs:
        walls.append(Walls(space, wall_defns[wall_ref]))
#   #
#   if jdat["walls"] == 1:
#       walls = Walls(space)
#   else:
#       walls = None
#   #

    goals = []
    for pargs, kwargs in jdat["goals"]:
        goals.append(Goal(space, *pargs, **kwargs))
    #
    blobs = []
    for pargs, kwargs in jdat["blobs"]:
        # Increase the blob elasticity as the round increases.
        kwargs["elasticity"] = kwargs.get("elasticity", 1.0) + round/10.0
        blobs.append(Blob(space, *pargs, **kwargs))
    #
    balls = []
    for pargs, kwargs in jdat["balls"]:
        balls.append(Ball(None, space, *pargs, **kwargs))
    # 


    zzzs = []
    for pargs, kwargs in jdat.get("zzzs", []):
        zzzs.append(ZZZ(space, *pargs, **kwargs))

    return Level(space, walls, goals, blobs, balls, zzzs)


def make_level_from_json_file(filename, round):
    with open(filename) as fp:
        jdat = json.load(fp)
    return make_level_from_json(jdat, round)



class Timer:
    def __init__(self, reverse=False):
        self.color = THECOLORS["yellow"]
        self.reverse = reverse
        self.ticks = 0
        self.label = None
        self.font = pygame.font.SysFont(None, 50)

    def start(self, seconds, label=None):
        self.label = label
        self.ticks = 0
        self.max_ticks = seconds * TICK
        if self.label:
            self.rendered_label = self.font.render(self.label, True, (255,255,255))

    def update(self, ticks):
        self.ticks += ticks

    def finished(self):
        return (self.ticks >= self.max_ticks)
        
    def remaining(self):
        return (self.max_ticks - self.ticks) / TICK

    def draw(self, surface):
        if not self.reverse:
            radius =  3 + 20 - 20* (self.ticks / float(self.max_ticks))
        else:
            radius =  3 + 20 * (self.ticks / float(self.max_ticks))
        p = surface.get_rect().center
        if Globals.gfxdraw:
            pygame.gfxdraw.aacircle(surface, p[0], p[1], int(radius), self.color)
        else:
            pygame.draw.circle(surface, self.color, p, int(radius), 3)
        if self.label:
            box = self.rendered_label.get_rect()
            box.center = surface.get_rect().center
            box.centery -= 100
            surface.blit(self.rendered_label, box)




class GetReadyText:
    def __init__(self):
        font = pygame.font.SysFont(None, 50)
        text = "Get Ready"
        self.rendered = font.render(text, True, (255,255,255))

    def draw(self, surface):
        box = self.rendered.get_rect()
        box.center = surface.get_rect().center
        box.centery -= 50
        surface.blit(self.rendered, box)


class Scorer:
    def __init__(self):
        self.score = 0
        self.multiplier = 1
        self._high_score = 0
        self._font = pygame.font.SysFont(None, 30)
        self.seconds_left = 0

    def draw(self, surface):
        score_render = self._font.render("%d" % self.score, True, (255,255,255))
        score_box = score_render.get_rect()
        score_box.left = 5
        score_box.centery = 20
        surface.blit(score_render, score_box)

        high_score_render = self._font.render("High Score: %d" % self._high_score, True, (255,255,255))
        high_score_box = high_score_render.get_rect()
        high_score_box.center = surface.get_rect().center
        high_score_box.centery = 20
        surface.blit(high_score_render, high_score_box)

        timer_render = self._font.render("%8.3f" % self.seconds_left, True, (255,255,255))
        timer_box = timer_render.get_rect()
        timer_box.topright = surface.get_rect().topright
        timer_box.centery = 20
        timer_box.right -= 5
        surface.blit(timer_render, timer_box)

    def start_timer(self, seconds):
        self.seconds_left = float(seconds)

    def update(self, points, seconds_elapsed):
        self.score += points * self.multiplier
        self._high_score = max(self._high_score, self.score)
        self.seconds_left = max(0, self.seconds_left-seconds_elapsed)

"""
IN_BETWEEN_LEVELS
STARTING_LEVEL
IN_LEVEL
FINISHING_LEVEL

timer
finish_timer
level
scorer
level_idx

IN_BETWEEN_LEVELS -> STARTING_LEVEL : level, level_idx, timer

STARTING_LEVEL -> IN_LEVEL :
    start scorer's timer

IN_LEVEL -> FINISHING_LEVEL :

FINISHING_LEVEL|RESTARTING_LEVEL -> IN_BETWEEN_LEVELS :
    level_idx -> next|same
    level -> load
    timer -> start

IN_LEVEL -> RESTARTING_LEVEL
    finish_timer -> start
"""

class LevelManager:
    def __init__(self, pattern):
        self.pattern = pattern
        self._refresh()

    def _refresh(self):
        self.levels = glob.glob(self.pattern)

    def get(self, level_idx, round):
        self._refresh()
        level_file = self.levels[level_idx]
        level = make_level_from_json_file(level_file, round)
        print >>sys.stderr, "+++ %s +++" % (level_file,)
        return level
        
    def __len__(self):
        self._refresh()
        return len(self.levels)


def main():
    pygame.init()
#   screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(sys.argv[0])

    get_ready_text = GetReadyText()
    global scorer
    scorer = Scorer()

    clock = pygame.time.Clock()
    timer = Timer()
    finish_timer = Timer(reverse=True)

    level_mgr = LevelManager(os.path.join(GAMEDIR, "level-*.json"))

    round = 1

    level_idx = 0
    level = level_mgr.get(level_idx, round)
    timer.start(WAIT, "Level %s Round %s" % (level_idx, round))
    game_state = IN_BETWEEN_LEVELS

    running = True
    while running:

        if game_state == IN_BETWEEN_LEVELS:
            # Wait for timer to expire.
            if timer.finished():
                game_state = STARTING_LEVEL
            # Only handle quit event.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

        elif game_state == STARTING_LEVEL:
            scorer.start_timer(20)
            game_state = IN_LEVEL

        elif game_state == FINISHING_LEVEL:
            if finish_timer.finished():
                if level_idx+1 >= len(level_mgr):
                    round += 1
                    scorer.multiplier = 1 + round/3.0
                level_idx = (level_idx + 1) % len(level_mgr)
                level = level_mgr.get(level_idx, round)
                timer.start(WAIT, "Level %s Round %s" % (level_idx, round))
                game_state = IN_BETWEEN_LEVELS

        elif game_state == RESTARTING_LEVEL:
            if finish_timer.finished():
                level = level_mgr.get(level_idx, round)
                timer.start(WAIT, "Level %s Round %s" % (level_idx, round))
                game_state = IN_BETWEEN_LEVELS

        elif game_state == IN_LEVEL:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                    Globals.debug = (Globals.debug+1) % 2                
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_g:
                    Globals.gfxdraw = (Globals.gfxdraw+1) % 2                
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_x:
                    round += 1
                # Level navigation
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    level = level_mgr.get(level_idx, round)
                    timer.start(WAIT, "Level %s Round %s" % (level_idx, round))
                    game_state = IN_BETWEEN_LEVELS
                    # need to tear down previous Level???
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                    level_idx = (level_idx + 1) % len(level_mgr)
                    level = level_mgr.get(level_idx, round)
                    timer.start(WAIT, "Level %s Round %s" % (level_idx, round))
                    game_state = IN_BETWEEN_LEVELS
                    # need to tear down previous Level???
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    level_idx = (level_idx - 1) % len(level_mgr)
                    level = level_mgr.get(level_idx, round)
                    timer.start(WAIT, "Level %s Round %s" % (level_idx, round))
                    game_state = IN_BETWEEN_LEVELS
                    # need to tear down previous Level???
                # Game actions
                elif event.type == pygame.MOUSEMOTION and event.buttons[0]: #[0]=left
                    level.blobs[level.blob_idx].add2(from_pygame(event.pos))
                elif event.type == pygame.MOUSEBUTTONUP and event.button == LEFTBUTTON:
                    # Switch to controlling next blob.
                    level.blob_idx = (level.blob_idx + 1) % len(level.blobs)


        screen.fill(THECOLORS["black"])
        level.draw(screen)
            
        if Globals.debug:
            pymunk.pygame_util.draw(screen, level.space)

        if game_state == IN_LEVEL:
            eol_points = 0
            if sum([getattr(t, "done", 0) for t in level.balls]) == len(level.balls):
                finish_timer.start(1.0, "Good job!")
                game_state = FINISHING_LEVEL
                eol_points = scorer.seconds_left*50*((round+1)*0.5)
            scorer.update(eol_points, 1/float(TICK))
            if level.update():  # True -> needs restart
                finish_timer.start(1.0, "Out of Bounds")
                game_state = RESTARTING_LEVEL
        elif game_state == IN_BETWEEN_LEVELS:
            timer.draw(screen)
            get_ready_text.draw(screen)
        elif game_state == STARTING_LEVEL:
            pass
        elif game_state in (FINISHING_LEVEL, RESTARTING_LEVEL):
            finish_timer.draw(screen)

        scorer.draw(screen)

        pygame.display.flip()
        ms_elapsed = clock.tick(TICK)

        timer.update((ms_elapsed/1000.0)*TICK) # FINISH: does flip() returns the elapsed time?
        finish_timer.update((ms_elapsed/1000.0)*TICK) # FINISH: does flip() returns the elapsed time?
        pygame.event.pump()


if __name__ == '__main__':
    GAMEDIR = os.path.dirname(os.path.abspath(sys.argv[0]))
    sys.exit(main())

