from src.physics import vector
import math
from src import constants

class Mover:
    MASS = 1.0
    FRICTION = 0.9
    TOUCHING_DAMAGE = 0
    IS_OBJECT = True

    def __init__(self, pos):
        self.pos = pos
        self.velocity = vector.Vectors()
        self.force = vector.Vectors()


    def apply_force(self, force):
        self.force.add(force)

    def on_update(self):
        pass

    def update(self):
        self.on_update()
        self.velocity.add(self.force.get_net_vector(1 / self.MASS))
        self.force.clear()
        self.velocity.reset(self.FRICTION)
        vx, vy = self.velocity.get_net_coordinates()
        self.pos = (self.pos[0] + vx, self.pos[1] + vy)
        self.pos = (max(-constants.MOVER_POS, min(constants.MOVER_POS, self.pos[0])), max(-constants.MOVER_POS, min(constants.MOVER_POS, self.pos[1])))
        self.on_update()

    def momentum(self, rot):
        return self.velocity.get_net_value() * self.MASS #* math.cos(math.radians(rot - self.velocity.get_net_rotation()))

    def object_gravitational(self, other: 'Mover'):
        if other is self:
            return
        if self.MASS > other.MASS:
            return False
        if not self.IS_OBJECT or not other.IS_OBJECT:
            return False
        r = (other.pos[0] - self.pos[0]) ** 2 + (other.pos[1] - self.pos[1]) ** 2
        G = .012
        if not r:
            return False
        self.force.add(vector.Vector(vector.coordinate_rotation(other.pos[0] - self.pos[0], other.pos[1] - self.pos[1]), G * self.MASS * other.MASS / r))
        return False

    def object_collision(self, other: 'Mover', required_distance: float):
        if other is self:
            return False
        if self.MASS > other.MASS:
            return False
        if not self.IS_OBJECT or not other.IS_OBJECT:
            return False
        r = (other.pos[0] - self.pos[0]) ** 2 + (other.pos[1] - self.pos[1]) ** 2
        d = math.sqrt(r)
        if d < required_distance:
            rot = vector.coordinate_rotation(other.pos[0] - self.pos[0], other.pos[1] - self.pos[1])
            self.velocity.add(vector.Vector(rot,
                                            max(-50, -(required_distance - d) / 80 + other.velocity.get_net_value() * math.cos(math.radians(rot - self.velocity.get_net_rotation())) / 30)))
            return True
        return False