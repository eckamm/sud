from poc1_header import *


class ZZZ:
    def __init__(self, space, coord):
        coord = tuple(coord)
        # rc == rotation center
        rc_body = pymunk.Body()
        rc_body.position = coord

        body = pymunk.Body(10, 10000)
        body.position = coord
        seg = pymunk.Segment(body, (0, 0), (0, 50), 5)
        seg.friction = FRICTION
        seg.elasticity = ELASTICITYW
        seg.collision_type = CT_ZZZ

        rc_joint = pymunk.PinJoint(body, rc_body, (0,0), (0,0))
        rc_joint = pymunk.PivotJoint(body, rc_body, (0,0), (0,0))
        space.add(body, seg, rc_joint)

        self.seg = seg # this is the Segment; use it to draw

    def draw(self, screen):
        seg = self.seg
        body = seg.body
        pv1 = body.position + seg.a.rotated(body.angle) # 1
        pv2 = body.position + seg.b.rotated(body.angle)

        p1 = to_pygame(pv1) # 2
        p2 = to_pygame(pv2)

        pygame.draw.lines(screen, THECOLORS["yellow"], False, [p1,p2])


