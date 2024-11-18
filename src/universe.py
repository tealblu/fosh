import random
from src import PALETTE
from src import fosh
from src.food import Food
from src import FOSH_VEL
from random import choice
import numpy as np
import time




def _angle(x):
    return np.arctan2(x[1], x[0])


def _norm(x):
    return x if np.allclose(x, 0) else x / np.linalg.norm(x)

class Universe():
    def __init__(self,
                 canvas,
                 edge_behaviour="avoid",
                 nearby_method="dist",
                 view_dist=80.0,
                 num_neighbors=5,
                 sep=1.5,
                 align=1,
                 cohes=1,
                 food_weight=1.5,
                 food_spawn_interval=30,
                 food_dist=300):
        self.foshs = []
        self.food = []
        self.canvas = canvas

        self.nearby_method = nearby_method
        self.view_dist = view_dist
        self.num_neighbors = num_neighbors

        self.edge_behaviour = edge_behaviour
        self.weights = {
            "seperation": sep,
            "alignment": align,
            "cohesion": cohes,
            "food": food_weight
        }

        self.food_spawn_interval = food_spawn_interval  # in seconds
        self.last_food_spawn_time = time.time()
        self.last_food_pos = None
        self.food_dist = food_dist

    def add_fosh(self, color=None, pos=None, angle=None):
        color = color or choice(PALETTE["accents"])
        pos = pos or self.canvas.size * (1 - 2 * np.random.random(self.canvas.size.shape))
        angle = angle or (2 * np.pi * np.random.random())
        self.foshs.append(fosh(color, pos, angle))

    def populate(self, n):
        for _ in range(n):
            self.add_fosh()

    
    def spawn_food(self):
        grid_size = 100  # Size of each grid cell
        canvas_size = np.array(self.canvas.size)  # Ensure canvas size is a numpy array

        # Cast the result to integer for the random.randint
        max_x = int(canvas_size[0] // grid_size)
        max_y = int(canvas_size[1] // grid_size)
        
        # minimum x and y are the negative canvas size
        min_x = 0 - int(canvas_size[0] // grid_size)
        min_y = 0 - int(canvas_size[1] // grid_size)
        
        # Cut off the most extreme 10% of the canvas
        max_x = int(max_x * 0.9)
        max_y = int(max_y * 0.9)
        min_x = int(min_x * 0.9)
        min_y = int(min_y * 0.9)

        loops = 0
        while True:
            # Generate random position for food within canvas bounds
            x_pos = random.randint(min_x, max_x - 1) * grid_size
            y_pos = random.randint(min_y, max_y - 1) * grid_size
            
            is_near_fosh = False
            for fosh in self.foshs:
                if fosh.dist(np.array([x_pos, y_pos])) < 3:
                    is_near_fosh = True
                    
            if not is_near_fosh:
                break
            
            loops += 1
            if loops > 100:
                print("Could not spawn food optimally. Spawning randomly.")
                break

        food_position = np.array([x_pos, y_pos])
        food = Food(pos=food_position)
        self.food = food.sprinkle(self.canvas, food_position, 10, self.food)



    def get_nearby(self, fosh):
        if self.nearby_method == "dist":
            out = []
            for other in self.foshs:
                if fosh.dist(other.pos) < self.view_dist and fosh is not other:
                    out.append(other)
            return out
        elif self.nearby_method == "count":
            return sorted((other for other in self.foshs if other is not fosh),
                         key=lambda other: fosh.dist(other.pos))[:self.num_neighbors]

    def reorient(self, fosh):
        """
        Calculates the new direction of the fosh with 5 rules: cohesion,
        separation, alignment, food attraction, and crowding avoidance.
        """
        # Get nearby foshs
        nearby = self.get_nearby(fosh)

        avg_pos = np.array((0, 0), dtype="float")  # cohesion
        avg_dir = np.array((0, 0), dtype="float")  # alignment
        avoid_foshs = np.array((0, 0), dtype="float")  # separation
        avoid_walls = np.array((0, 0), dtype="float")  # wall avoidance
        food_attraction = np.array((0, 0), dtype="float")  # food attraction
        crowding_avoidance = np.array((0, 0), dtype="float")  # crowding avoidance

        # Crowding parameters
        max_flock_size = 10
        crowding_radius = 150  # Larger radius to evaluate total density

        # Calculate fosh behaviors
        if len(nearby) != 0:
            for i, other in enumerate(nearby):
                diff = other.pos - fosh.pos

                avg_pos += (diff - avg_pos) / (i + 1)  # running average for cohesion
                avg_dir += (other.dir - avg_dir) / (i + 1)  # running average for alignment
                avoid_foshs -= diff / np.dot(diff, diff)  # separation

            # Normalize behaviors
            avg_pos = _norm(avg_pos)
            avg_dir = _norm(avg_dir)
            avoid_foshs = _norm(avoid_foshs)

        # Check for overall density in a larger radius
        density = sum(1 for other in self.foshs if fosh.dist(other.pos) < crowding_radius and fosh is not other)
        if density > max_flock_size:
            # Apply repulsion from the center of all nearby foshs in the larger radius
            center_of_mass = np.mean([other.pos for other in self.foshs if fosh.dist(other.pos) < crowding_radius], axis=0)
            crowding_avoidance = _norm(fosh.pos - center_of_mass)

        # Handle wall avoidance
        if self.edge_behaviour == "avoid" and (np.abs(fosh.pos) > self.canvas.size - self.view_dist).any():
            for i, (coord, lower, upper) in enumerate(zip(fosh.pos, -self.canvas.size, self.canvas.size)):
                if (diff := coord - lower) < self.view_dist:
                    avoid_walls[i] += np.abs(1 / diff)
                if (diff := upper - coord) < self.view_dist:
                    avoid_walls[i] -= np.abs(1 / diff)

        # Calculate food attraction
        if self.food:
            closest_food = min(self.food, key=lambda f: fosh.dist(f.pos))
            if fosh.dist(closest_food.pos) <= self.food_dist:
                direction_to_food = closest_food.pos - fosh.pos
                food_attraction = _norm(direction_to_food)
                
                if fosh.speed < FOSH_VEL * 2:
                    fosh.speed *= 1.05
        else:
            if fosh.speed > FOSH_VEL:
                fosh.speed *= 0.95

        # Combine all behaviors
        sum_vector = (_norm(avoid_walls) +
                    self.weights["seperation"] * avoid_foshs +
                    self.weights["cohesion"] * avg_pos +
                    self.weights["alignment"] * avg_dir +
                    crowding_avoidance)  # Add crowding avoidance

        if self.food:
            sum_vector += self.weights["food"] * food_attraction

        sum_vector = _norm(sum_vector)

        if np.allclose(sum_vector, 0):
            return fosh.angle
        else:
            return _angle(sum_vector)



    def draw(self):
        self.canvas.fill(PALETTE["background"])
        for fosh in self.foshs:
            fosh.draw(self.canvas)
        for food in self.food:
            food.draw(self.canvas)
        self.canvas.update()

    def tick(self):
        # Spawn food at intervals
        current_time = time.time()
        if current_time - self.last_food_spawn_time >= self.food_spawn_interval:
            self.spawn_food()
            self.last_food_spawn_time = current_time

        # Calculate new directions
        angles = []
        for fosh in self.foshs:
            angles.append(self.reorient(fosh))

        for fosh, angle in zip(self.foshs, angles):
            if self.edge_behaviour == "wrap":
                self.wrap(fosh)
            fosh.turn_to(angle, 1 / self.canvas.fps)
            fosh.tick(1 / self.canvas.fps)

        # Check if any fosh has reached food
        self.check_food_consumption()

    def check_food_consumption(self):
        consumption_radius = 10  # Define how close a fosh needs to be to consume food
        for fosh in self.foshs:
            for food in self.food:
                if fosh.dist(food.pos) < consumption_radius:
                    self.food.remove(food)
                    # Optionally, add behaviors like increasing fosh's speed or energy
                    break  # Assuming one food consumed at a time

    def wrap(self, fosh):
        fosh.pos = (fosh.pos + self.canvas.size) % (2 * self.canvas.size) - self.canvas.size

    def loop(self):
        while self.canvas.is_open():
            self.draw()
            self.tick()
