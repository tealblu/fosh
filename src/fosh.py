import datetime
from random import choice
from src import FOSH_VEL, FOSH_TURN_SPEED, PALETTE, FOSH_TAIL_LEN, FOSH_SIZE, SATURATION
import numpy as np


def _unit_vector(angle):
    return np.array([np.cos(angle), np.sin(angle)], dtype="float")


class fosh():
    def __init__(self, color, pos, angle=0, speed=FOSH_VEL):
        self.pos = np.array(pos, dtype="float")
        self.angle = angle % (2 * np.pi)
        self.color = color
        self.speed = speed
        self.last_bite = datetime.datetime.now() - datetime.timedelta(seconds=SATURATION)

    @property
    def dir(self):
        return _unit_vector(self.angle)

    @property
    def vel(self):
        return self.speed * self.dir
        
    @property
    def is_hungry(self):
        return datetime.datetime.now() - self.last_bite > datetime.timedelta(seconds=SATURATION)

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
        # Draw the circular body
        circle_center = self.pos
        circle_radius = FOSH_SIZE
        canvas.draw_circle(circle_radius, circle_center, self.color)

        # Calculate the tail position on the edge of the circle
        tail_mesh = 10
        tail_base = circle_center - ( circle_radius - tail_mesh ) * _unit_vector(self.angle)
        tail_angle = self.angle + np.pi
        tail_tip = tail_base
        
        # Calculate the left and right points for the tail
        spread_angle = np.pi / 8 # reduce to make points closer
        tail_left = tail_base + FOSH_TAIL_LEN * _unit_vector(tail_angle + spread_angle)
        tail_right = tail_base + FOSH_TAIL_LEN * _unit_vector(tail_angle - spread_angle)
        
        # Draw the tail
        tail = [tail_tip, tail_left, tail_right]
        canvas.draw_poly(tail, self.color)


    def tick(self, dt):
        self.pos += self.vel * dt

