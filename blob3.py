from poc1_header import *

"""

the pieces of the blob age and disappear


"""


class Blob3:
    def __init__(self, space, max_data=15, radius=20, color="blue", 
                 elasticity=ELASTICITYB, fade=False, dynamic=False):
        self.fade = fade # Does the blob fade away?
        self.dynamic = dynamic
        self.elasticity = elasticity
        self.space = space
        self.color = THECOLORS[color]
        self.data = [] # list of tuples of (coord, shape)
        self.max_data = max_data
        self.radius = radius
        self.counter = 0


    def add(self, coord):
        if len(self.data) >= self.max_data:
            return

        mass = 1
        inertia = pymunk.moment_for_circle(mass, 0, self.radius) # 1
        if self.dynamic:
            body = pymunk.Body(mass, inertia) # 2 dynamic
        else:
            body = pymunk.Body() # 2 static
        body.position = coord
        shape = pymunk.Circle(body, self.radius)
        shape.elasticity = self.elasticity
        shape.friction = FRICTION
        shape.collision_type = CT_BLOB
        if self.dynamic:
            self.space.add(shape, body)
        else:
            self.space.add(shape)
        self.data.append(shape)
        # just added as data[-1]

        if len(self.data) >= 2:
            shape1 = self.data[-1]
            shape2 = self.data[-2]
            body1 = shape1.body
            body2 = shape2.body
#           print >>sys.stderr, body1.position, body2.position
            minlen = 3 + shape1.radius + shape2.radius
            maxlen = 3 + shape1.radius + shape2.radius
#           joint = pymunk.PivotJoint(body1, body2, (0,0), (0,0))
#           joint = pymunk.PivotJoint(body1, body2, (-shape1.radius*2,0), (shape2.radius*2,0)) 
            if self.dynamic: 
                joint = pymunk.SlideJoint(body1, body2, (0,0), (0,0), minlen, maxlen) 
    #           joint = pymunk.PinJoint(body1, body2, (0,0), (0,0))
                body2.joint = joint # remove this when body2 is removed
                self.space.add(joint)

#       for i, shape in enumerate(self.data):
#           print >>sys.stderr, i, shape, getattr(shape.body, "joint", None)


    def add2(self, coord):
        if len(self.data) >= self.max_data:
            if hasattr(self.data[0].body, "joint"):
                self.space.remove(self.data[0].body.joint)
            if self.dynamic:
                self.space.remove(self.data[0].body)
            self.space.remove(self.data[0])
            del self.data[0]
        self.add(coord) 

    def draw(self, surface):
        for shape in self.data:
            coord = shape.body.position
            p = ( int(coord[0]), 
                  SCREEN_HEIGHT-int(coord[1]) )
            if Globals.gfxdraw:
                pygame.gfxdraw.aacircle(surface, p[0], p[1], int(shape.radius), self.color)
            else:
                pygame.draw.circle(surface, self.color, p, int(shape.radius), 2)

    def update(self):
#       return 
#       for i, shape in enumerate(self.data):
#           print >>sys.stderr, i, shape, getattr(shape.body, "joint", None)
        self.counter += 1
        if self.fade:
            if ( self.counter % 2 ) == 0:
                if self.data:
                    if hasattr(self.data[0].body, "joint"):
                        self.space.remove(self.data[0].body.joint)
                    if self.dynamic:
                        self.space.remove(self.data[0].body)
                    self.space.remove(self.data[0])
                    del self.data[0]


