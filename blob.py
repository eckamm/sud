from poc1_header import *


class Blob:
    def __init__(self, space, max_data=15, radius=20, color="blue", elasticity=ELASTICITYB):
        self.elasticity = elasticity
        self.space = space
        self.color = THECOLORS[color]
        self.data = [] # list of tuples of (coord, shape)
        self.max_data = max_data
        self.radius = radius

    def add(self, coord):
        if len(self.data) >= self.max_data:
            return
        body = pymunk.Body() # static
        body.position = coord
        shape = pymunk.Circle(body, self.radius)
        shape.elasticity = self.elasticity
        shape.friction = FRICTION
        shape.collision_type = CT_BLOB
        self.space.add(shape)
        self.data.append((coord, shape))

    def add2(self, coord):
        if len(self.data) >= self.max_data:
            self.space.remove(self.data[0][1])
            del self.data[0]
        self.add(coord) 

    def draw(self, surface):
        for coord, shape in self.data:
            p = ( int(coord[0]), 
                  SCREEN_HEIGHT-int(coord[1]) )
            if Globals.gfxdraw:
                pygame.gfxdraw.aacircle(surface, p[0], p[1], self.radius, self.color)
            else:
                pygame.draw.circle(surface, self.color, p, self.radius, 2)

    def update(self):
        pass
