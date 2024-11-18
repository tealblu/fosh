from cv2 import VideoWriter, VideoWriter_fourcc as FourCC
from src import SCALE, OUT_DIR
from time import strftime, localtime
import cv2
import numpy as np


TRANSLATION = np.array((SCALE, -SCALE))  # y coord is negative as the y axis is in downward direction in images


class Canvas():
    def __init__(self, res, fps):
        # output related
        self.res = np.array(res, dtype="int")
        self.fps = float(fps)
        self.current_frame = self.new_frame()
        self.closed = False

        # renderer
        self.filename = OUT_DIR + strftime('%Y%m%dT%H%M%S', localtime()) + ".mp4"
        self.title = f"Boids - Preview - {self.filename}"
        self.video = VideoWriter(self.filename, FourCC(*"mp4v"), int(self.fps), tuple(self.res))
     
    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        cv2.destroyWindow(self.title)
        self.video.release()

    @property
    def size(self):
        return np.abs(self.from_px(self.res))

    def to_px(self, pos):
        return (pos / TRANSLATION + self.res / 2).astype("int")

    def from_px(self, px):
        return (px.astype("float") - self.res / 2) * TRANSLATION

    def is_open(self):
        return not self.closed

    def new_frame(self):
        return np.ndarray(shape=(*self.res[::-1], 3), dtype="uint8")

    def update(self):
        self.video.write(self.current_frame)
        cv2.imshow(self.title, self.current_frame)
        self.current_frame = self.new_frame()

        # set to true if window-x or {esc, ctrl-c, q} pressed
        self.closed |= (cv2.getWindowProperty(self.title, 0) < 0) or (cv2.waitKey(int(1000 / self.fps)) in {27, 2, 3, ord("q"), ord("Q")})

    def fill(self, color):
        self.current_frame[:, :] = np.array(color, dtype="uint8")

    def draw_poly(self, points, color):
        cv2.fillPoly(self.current_frame,
                     [np.array([self.to_px(p) for p in points])],  # double list as fillPoly expects a list of polygons
                     color,
                     16)  # = antialiased
