from os.path import join
import numpy as np


DEFAULT_VIEW_DIST = 80.0
DEFAULT_NUM_NEIGHBORS = 5

fosh_VEL = 90
fosh_NOSE_LEN = 30
fosh_TURN_SPEED = 3.6
fosh_TAIL_LEN = 10

OUT_DIR = join(".", "out", "")
SCALE = 1.0  # in px/unit
PALETTE = {  # in bgr (expected by opencv)
    "background": (0x2A, 0x18, 0x0B),
    "highlight":  (0x60, 0x70, 0xf8),
    "accents":   [(0xc2, 0xc7, 0xef),
                  (0xd6, 0xd7, 0xcd),
                  (0xd4, 0xe5, 0xff)],
    "food":      (0xff, 0xff, 0x00)}


from src.fosh import fosh
from src.canvas import Canvas
from src.universe import Universe
