from cv2 import VideoWriter, VideoWriter_fourcc as FourCC
from src import SCALE, OUT_DIR
from time import strftime, localtime
import cv2
import numpy as np

TRANSLATION = np.array((SCALE, -SCALE))  # y coord is negative as the y axis is in downward direction in images

class Canvas():
    @staticmethod
    def parse_resolution(res):
        """Convert various resolution inputs into a tuple of integers"""
        if isinstance(res, (tuple, list)):
            return tuple(map(int, res))
        if isinstance(res, str):
            return tuple(map(int, res.split('x')))
        raise ValueError("Resolution must be either 'WxH' string or [W,H] list/tuple")

    def __init__(self, res, fps, video=False):
        # Parse and validate resolution
        try:
            self.res = np.array(self.parse_resolution(res), dtype=np.int32)
            if len(self.res) != 2 or any(self.res <= 0):
                raise ValueError("Resolution must be two positive integers")
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid resolution format: {res}. Use 'WxH' or [W,H]") from e

        self.fps = float(fps)
        self.closed = False
        
        # renderer
        self.filename = OUT_DIR + strftime('%Y%m%dT%H%M%S', localtime()) + ".mp4"
        self.title = f"foshs - Preview - {self.filename}"
        
        # Explicitly create window and set it up
        cv2.namedWindow(self.title, cv2.WINDOW_AUTOSIZE)
        
        # Initialize video writer if needed
        if video:
            self.video = VideoWriter(
                self.filename,
                FourCC("mp4v"),
                int(self.fps),
                tuple(self.res)
            )
        else:
            self.video = None
            
        # Create initial frame
        self.current_frame = self.new_frame()
        
        # Initial display to ensure window creation
        self.update()
        
    def __enter__(self):
        return self
        
    def __exit__(self, *args, **kwargs):
        if self.video is not None:
            self.video.release()
        cv2.destroyAllWindows()  # More reliable than destroying single window
        
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
        # Create frame with correct dimensions (height, width, channels)
        return np.zeros((self.res[1], self.res[0], 3), dtype=np.uint8)
        
    def update(self):
        if self.closed:
            return False
            
        # Write frame to video if recording
        if self.video is not None:
            self.video.write(self.current_frame)
            
        # Show current frame
        cv2.imshow(self.title, self.current_frame)
        
        # Handle window closing and key events
        key = cv2.waitKey(max(1, int(1000 / self.fps))) & 0xFF
        self.closed = (key in {27, 2, 3, ord("q"), ord("Q")})
        
        # Additional check for window closing
        try:
            visible = cv2.getWindowProperty(self.title, cv2.WND_PROP_VISIBLE)
            if visible < 1.0:
                self.closed = True
        except cv2.error:
            self.closed = True
            
        # Prepare next frame if window is still open
        if not self.closed:
            self.current_frame = self.new_frame()
            
        return not self.closed
        
    def fill(self, color):
        self.current_frame[:, :] = np.array(color, dtype="uint8")
        
    def draw_poly(self, points, color):
        cv2.fillPoly(
            self.current_frame,
            [np.array([self.to_px(p) for p in points])],
            color,
            cv2.LINE_AA
        )
        
    def draw_sprite(self, sprite, position, scale=1.0, rotation=0.0):
        """
        Draws a sprite onto the canvas with scaling and rotation.

        :param sprite: The sprite image (as a NumPy array with an optional alpha channel).
        :param position: The (x, y) position to place the sprite (centered).
        :param scale: Scaling factor for the sprite.
        :param rotation: Rotation angle in degrees.
        """
        # Resize the sprite
        sprite = cv2.resize(sprite, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)

        # Rotate the sprite
        if rotation != 0:
            center = (sprite.shape[1] // 2, sprite.shape[0] // 2)
            rotation_matrix = cv2.getRotationMatrix2D(center, -rotation, 1.0)
            sprite = cv2.warpAffine(sprite, rotation_matrix, (sprite.shape[1], sprite.shape[0]))

        # Sprite dimensions
        sprite_h, sprite_w = sprite.shape[:2]
        x, y = self.to_px(position)

        # Calculate overlay region
        x1 = max(0, x - sprite_w // 2)
        y1 = max(0, y - sprite_h // 2)
        x2 = min(self.res[0], x + sprite_w // 2)
        y2 = min(self.res[1], y + sprite_h // 2)

        # Adjust sprite region if it goes out of bounds
        sprite_x1 = max(0, -x + sprite_w // 2)
        sprite_y1 = max(0, -y + sprite_h // 2)
        sprite_x2 = sprite_x1 + (x2 - x1)
        sprite_y2 = sprite_y1 + (y2 - y1)

        # Validate regions to avoid zero-width/height issues
        if x1 >= x2 or y1 >= y2 or sprite_x1 >= sprite_x2 or sprite_y1 >= sprite_y2:
            return  # Nothing to draw; skip this sprite

        canvas_region = self.current_frame[y1:y2, x1:x2]
        sprite_region = sprite[sprite_y1:sprite_y2, sprite_x1:sprite_x2]

        # Handle transparency blending
        if sprite.shape[2] == 4:  # Check for alpha channel
            alpha = sprite_region[:, :, 3] / 255.0  # Normalize alpha channel
            alpha = np.squeeze(alpha)
            for c in range(3):  # Blend RGB channels
                canvas_region[:, :, c] = (
                    alpha * sprite_region[:, :, c] + (1 - alpha) * canvas_region[:, :, c]
                )
        else:
            canvas_region[:, :, :] = sprite_region[:, :, :3]  # No alpha, just overlay



    def load_sprite(self, filepath):
        """
        Loads a sprite from the given file path.

        :param filepath: Path to the image file.
        :return: Loaded sprite as a NumPy array with an alpha channel.
        """
        sprite = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)  # Load with alpha channel
        if sprite is None:
            raise FileNotFoundError(f"Could not load sprite: {filepath}")
        return sprite