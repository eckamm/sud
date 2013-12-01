from poc1_header import *


class Goal:
    def __init__(self, space, coord0, coord1, coord2, color="blue"):
        assert tuple(coord1) == (0, 0)
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

        if (a-c) != 0:
            pygame.draw.lines(surface, self.color, False, [(a-m, b-m), (c+m, d-m)]) # top
            pygame.draw.lines(surface, self.color, False, [(a-m, b+m), (c+m, d+m)]) # bottom
            pygame.draw.lines(surface, self.color, False, [(a-m, b-m), (a-m, b+m)]) # left
            pygame.draw.lines(surface, self.color, False, [(c+m, d-m), (c+m, d+m)]) # right
        else:
            pygame.draw.lines(surface, self.color, False, [(a-m, b+m), (a+m, b+m)]) # top
            pygame.draw.lines(surface, self.color, False, [(a+m, b+m), (c+m, d-m)]) # bottom
            pygame.draw.lines(surface, self.color, False, [(c+m, d-m), (c-m, d-m)]) # left
            pygame.draw.lines(surface, self.color, False, [(c-m, d-m), (a-m, b+m)]) # right



