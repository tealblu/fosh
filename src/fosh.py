from random import choice
from src import FOSH_VEL, FOSH_NOSE_LEN, FOSH_TURN_SPEED, PALETTE, FOSH_TAIL_LEN
import numpy as np


def _unit_vector(angle):
    return np.array([np.cos(angle), np.sin(angle)], dtype="float")


class fosh():
    def __init__(self, canvas, color, pos, angle=0, speed=FOSH_VEL, sprite_path="./src/fosh.png"):
        self.pos = np.array(pos, dtype="float")
        self.angle = angle % (2 * np.pi)
        self.color = color
        self.speed = speed
        self.sprite = canvas.load_sprite(sprite_path)

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
        """
        Draws the Fosh on the canvas using the sprite.

        :param canvas: Canvas object to render the Fosh.
        """
        # Sprite scaling factor (adjust as needed for desired size)
        scale = FOSH_NOSE_LEN / self.sprite.shape[0]
        
        # Convert angle (radians) to degrees for rotation
        rotation_deg = np.degrees(self.angle)

        # Draw the sprite
        canvas.draw_sprite(self.sprite, position=self.pos, scale=scale, rotation=rotation_deg)

    def tick(self, dt):
        self.pos += self.vel * dt

