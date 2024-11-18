from random import choice
from src import FOSH_VEL, FOSH_NOSE_LEN, FOSH_TURN_SPEED, PALETTE, FOSH_TAIL_LEN
import numpy as np


def _unit_vector(angle):
    return np.array([np.cos(angle), np.sin(angle)], dtype="float")


class fosh():
    def __init__(self, color, pos, angle=0, speed=FOSH_VEL):
        self.pos = np.array(pos, dtype="float")
        self.angle = angle % (2 * np.pi)
        self.color = color
        self.speed = speed

    @property
    def dir(self):
        return _unit_vector(self.angle)

    @property
    def vel(self):
        return self.speed * self.dir

    def dist(self, pos):
        return np.linalg.norm(self.pos - pos)

    def turn_by(self, dangle, dt):
        # dont turn too fast
        self.angle += np.clip(dangle, -dt * FOSH_TURN_SPEED, dt * FOSH_TURN_SPEED)

        # keep angle in range [0, 2pi)
        self.angle %= 2 * np.pi

    def turn_to(self, angle, dt):
        a = (angle - self.angle) % (2 * np.pi)
        b = -(-a % (2 * np.pi))
        self.turn_by(min(a, b, key=lambda x: np.abs(x)), dt)

    def draw(self, canvas):
        tip = self.pos + FOSH_NOSE_LEN * _unit_vector(self.angle)
        left = self.pos + FOSH_NOSE_LEN / 1.5 * _unit_vector(self.angle + np.pi / 4)
        right = self.pos + FOSH_NOSE_LEN / 1.5 * _unit_vector(self.angle - np.pi / 4)
        bottom = self.pos  # The bottom point is the same as the axis
        
        tail_len = FOSH_TAIL_LEN
        tail_pos = self.pos - tail_len * _unit_vector(self.angle)
        tail_angle = self.angle + np.pi
        tail = tail_pos - tail_len * _unit_vector(tail_angle)
        tail_left = tail_pos - tail_len / 2 * _unit_vector(tail_angle + 2 * np.pi / 3)
        tail_right = tail_pos - tail_len / 2 * _unit_vector(tail_angle - 2 * np.pi / 3)
        
        canvas.draw_poly([tail, tail_left, tail_right], self.color)
        
        canvas.draw_poly([tip, left, bottom, right], self.color)

    def tick(self, dt):
        self.pos += self.vel * dt

