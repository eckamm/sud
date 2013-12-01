"""
The idea is to have this module be a "common header" which
can be used as:
    from poc1_header import *
"""
import sys

import pygame
import pygame.gfxdraw
from pygame.color import THECOLORS

import pymunk
from pymunk.vec2d import Vec2d
import pymunk.pygame_util


from poc1_constants import *


class Globals:
    debug = 0
    gfxdraw = 0



def to_pygame(p):
    """Small hack to convert pymunk to pygame coordinates"""
    return int(p.x), int(-p.y+SCREEN_HEIGHT)


def from_pygame(p):
    """Small hack to convert pygame to pymunk coordinates"""
    return Vec2d(p[0], SCREEN_HEIGHT-p[1])


