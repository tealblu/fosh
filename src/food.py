from time import sleep
import numpy as np
from src import PALETTE


class Food:
    def __init__(self, pos=None, color=None, size=5):
        # Use np.array directly to handle the position
        self.pos = pos if pos is not None else np.random.uniform(-1, 1, size=2) * 400  # Adjust range as needed
        self.color = color or PALETTE["food"]  # Ensure PALETTE has a 'food' color
        self.size = size

    def draw(self, canvas):
        # Create a diamond shape for the food
        size = self.size  # Half-length of the diamond's diagonal
        top = self.pos + np.array([0, size])
        bottom = self.pos + np.array([0, -size])
        left = self.pos + np.array([-size, 0])
        right = self.pos + np.array([size, 0])
        canvas.draw_poly([top, right, bottom, left], self.color)
        
    def sprinkle(self, canvas, pos, x_count, food, food_spawn_chance):
        for _ in range(x_count):
            if np.random.random() < food_spawn_chance:
                # Randomly offset each food particle around the provided position
                new_pos = pos + np.random.uniform(-30, 30, size=2)  # Small random offset around the 'pos'
                sprinkle_food = Food(pos=new_pos, color=self.color, size=self.size)
                sprinkle_food.draw(canvas)
                food.append(sprinkle_food)
            
        return food