from src import PALETTE
from src import Boid
from src import BOID_VEL
from random import choice
import numpy as np
import time


def _angle(x):
    return np.arctan2(x[1], x[0])


def _norm(x):
    return x if np.allclose(x, 0) else x / np.linalg.norm(x)


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


class Universe():
    def __init__(self,
                 canvas,
                 edge_behaviour="avoid",
                 nearby_method="dist",
                 view_dist=80.0,
                 num_neighbors=5,
                 sep=1,
                 align=1,
                 cohes=1,
                 food_weight=1.5,
                 food_spawn_interval=3,
                 food_dist=200.0):
        self.boids = []
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
        self.food_dist = food_dist

    def add_boid(self, color=None, pos=None, angle=None):
        color = color or choice(PALETTE["accents"])
        pos = pos or self.canvas.size * (1 - 2 * np.random.random(self.canvas.size.shape))
        angle = angle or (2 * np.pi * np.random.random())
        self.boids.append(Boid(color, pos, angle))

    def populate(self, n):
        for _ in range(n):
            self.add_boid()

    def spawn_food(self):
        grid_size = 100  # Size of each grid cell
        canvas_size = np.array(self.canvas.size)  # Ensure canvas size is a numpy array
        num_cells = np.floor(canvas_size / grid_size).astype(int)  # Number of cells in each dimension

        # Initialize grid densities
        grid = np.zeros(num_cells)

        # Calculate grid cell indices for each boid
        for boid in self.boids:
            grid_x = int(boid.pos[0] // grid_size)  # Adjust if needed for canvas offset
            grid_y = int(boid.pos[1] // grid_size)

            # Ensure indices are within bounds
            grid_x = np.clip(grid_x, 0, num_cells[0] - 1)
            grid_y = np.clip(grid_y, 0, num_cells[1] - 1)

            grid[grid_x, grid_y] += 1  # Increment density for the cell

        # Find the cell with the fewest boids
        least_dense_cell = np.unravel_index(np.argmin(grid), grid.shape)

        # Calculate the center position of the least dense cell
        food_position = np.array([least_dense_cell[0] * grid_size + grid_size / 2, 
                                least_dense_cell[1] * grid_size + grid_size / 2])

        # Spawn food at the calculated position
        food = Food(pos=food_position)
        self.food.append(food)

    def get_nearby(self, boid):
        if self.nearby_method == "dist":
            out = []
            for other in self.boids:
                if boid.dist(other.pos) < self.view_dist and boid is not other:
                    out.append(other)
            return out
        elif self.nearby_method == "count":
            return sorted((other for other in self.boids if other is not boid),
                         key=lambda other: boid.dist(other.pos))[:self.num_neighbors]

    def reorient(self, boid):
        """
        Calculates the new direction of the boid with 5 rules: cohesion,
        separation, alignment, food attraction, and crowding avoidance.
        """
        # Get nearby boids
        nearby = self.get_nearby(boid)

        avg_pos = np.array((0, 0), dtype="float")  # cohesion
        avg_dir = np.array((0, 0), dtype="float")  # alignment
        avoid_boids = np.array((0, 0), dtype="float")  # separation
        avoid_walls = np.array((0, 0), dtype="float")  # wall avoidance
        food_attraction = np.array((0, 0), dtype="float")  # food attraction
        crowding_avoidance = np.array((0, 0), dtype="float")  # crowding avoidance

        # Crowding parameters
        max_flock_size = 10
        crowding_radius = 150  # Larger radius to evaluate total density

        # Calculate boid behaviors
        if len(nearby) != 0:
            for i, other in enumerate(nearby):
                diff = other.pos - boid.pos

                avg_pos += (diff - avg_pos) / (i + 1)  # running average for cohesion
                avg_dir += (other.dir - avg_dir) / (i + 1)  # running average for alignment
                avoid_boids -= diff / np.dot(diff, diff)  # separation

            # Normalize behaviors
            avg_pos = _norm(avg_pos)
            avg_dir = _norm(avg_dir)
            avoid_boids = _norm(avoid_boids)

        # Check for overall density in a larger radius
        density = sum(1 for other in self.boids if boid.dist(other.pos) < crowding_radius and boid is not other)
        if density > max_flock_size:
            # Apply repulsion from the center of all nearby boids in the larger radius
            center_of_mass = np.mean([other.pos for other in self.boids if boid.dist(other.pos) < crowding_radius], axis=0)
            crowding_avoidance = _norm(boid.pos - center_of_mass)

        # Handle wall avoidance
        if self.edge_behaviour == "avoid" and (np.abs(boid.pos) > self.canvas.size - self.view_dist).any():
            for i, (coord, lower, upper) in enumerate(zip(boid.pos, -self.canvas.size, self.canvas.size)):
                if (diff := coord - lower) < self.view_dist:
                    avoid_walls[i] += np.abs(1 / diff)
                if (diff := upper - coord) < self.view_dist:
                    avoid_walls[i] -= np.abs(1 / diff)

        # Calculate food attraction
        if self.food:
            closest_food = min(self.food, key=lambda f: boid.dist(f.pos))
            if boid.dist(closest_food.pos) <= self.food_dist:
                direction_to_food = closest_food.pos - boid.pos
                food_attraction = _norm(direction_to_food)
                
                boid.speed = BOID_VEL * 2
            else:
                boid.speed = BOID_VEL

        # Combine all behaviors
        sum_vector = (_norm(avoid_walls) +
                    self.weights["seperation"] * avoid_boids +
                    self.weights["cohesion"] * avg_pos +
                    self.weights["alignment"] * avg_dir +
                    crowding_avoidance)  # Add crowding avoidance

        if self.food:
            sum_vector += self.weights["food"] * food_attraction

        sum_vector = _norm(sum_vector)

        if np.allclose(sum_vector, 0):
            return boid.angle
        else:
            return _angle(sum_vector)



    def draw(self):
        self.canvas.fill(PALETTE["background"])
        for boid in self.boids:
            boid.draw(self.canvas)
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
        for boid in self.boids:
            angles.append(self.reorient(boid))

        for boid, angle in zip(self.boids, angles):
            if self.edge_behaviour == "wrap":
                self.wrap(boid)
            boid.turn_to(angle, 1 / self.canvas.fps)
            boid.tick(1 / self.canvas.fps)

        # Check if any boid has reached food
        self.check_food_consumption()

    def check_food_consumption(self):
        consumption_radius = 10  # Define how close a boid needs to be to consume food
        for boid in self.boids:
            for food in self.food:
                if boid.dist(food.pos) < consumption_radius:
                    self.food.remove(food)
                    # Optionally, add behaviors like increasing boid's speed or energy
                    break  # Assuming one food consumed at a time

    def wrap(self, boid):
        boid.pos = (boid.pos + self.canvas.size) % (2 * self.canvas.size) - self.canvas.size

    def loop(self):
        while self.canvas.is_open():
            self.draw()
            self.tick()
