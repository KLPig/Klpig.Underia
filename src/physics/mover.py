from src.physics import vector
import math

class Mover:
    MASS = 1.0
    FRICTION = 0.9
    TOUCHING_DAMAGE = 0

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
        self.on_update()

    def object_collide(self, other: 'Mover'):
        if other is self:
            return
        if (other.pos[0] - self.pos[0]) ** 2 + (other.pos[1] - self.pos[1]) ** 2 < ((math.sqrt(self.MASS) + math.sqrt(other.MASS)) / 2 + 24) ** 2:
            r = vector.coordinate_rotation(other.pos[0] - self.pos[0], other.pos[1] - self.pos[1])
            self.force.add(vector.Vector(r + 180, self.TOUCHING_DAMAGE * (self.MASS + other.MASS) / (self.MASS + other.MASS) * 5))
            return True
        r = (other.pos[0] - self.pos[0]) ** 2 + (other.pos[1] - self.pos[1]) ** 2
        G = .15
        self.force.add(vector.Vector(vector.coordinate_rotation(other.pos[0] - self.pos[0], other.pos[1] - self.pos[1]), G * self.MASS * other.MASS / r))
        return False