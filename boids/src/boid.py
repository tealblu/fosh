from random import choice
from src import BOID_VEL, BOID_NOSE_LEN, BOID_TURN_SPEED, PALETTE
import numpy as np


def _unit_vector(angle):
    return np.array([np.cos(angle), np.sin(angle)], dtype="float")


class Boid():
    def __init__(self, color, pos, angle=0):
        self.pos = np.array(pos, dtype="float")
        self.angle = angle % (2 * np.pi)
        self.color = color

    @property
    def dir(self):
        return _unit_vector(self.angle)

    @property
    def vel(self):
        return BOID_VEL * self.dir

    def dist(self, pos):
        return np.linalg.norm(self.pos - pos)

    def turn_by(self, dangle, dt):
        # dont turn too fast
        self.angle += np.clip(dangle, -dt * BOID_TURN_SPEED, dt * BOID_TURN_SPEED)

        # keep angle in range [0, 2pi)
        self.angle %= 2 * np.pi

    def turn_to(self, angle, dt):
        a = (angle - self.angle) % (2 * np.pi)
        b = -(-a % (2 * np.pi))
        self.turn_by(min(a, b, key=lambda x: np.abs(x)), dt)

    def draw(self, canvas):
        tip = self.pos + BOID_NOSE_LEN * self.dir
        left = self.pos + BOID_NOSE_LEN / 2 * _unit_vector(self.angle + 2 * np.pi / 3)
        right = self.pos + BOID_NOSE_LEN / 2 * _unit_vector(self.angle - 2 * np.pi / 3)
        canvas.draw_poly([tip, left, self.pos, right], self.color)

    def tick(self, dt):
        self.pos += self.vel * dt

