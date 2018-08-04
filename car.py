import random


class Car(object):

    def __init__(self, traffic_map, x=None, y=None):
        self.traffic_map = traffic_map
        self.x, self.y = self.place_car(x, y)
        self.red_light = any((self.x, self.y) == (i.x, i.y) for i in self.traffic_map.intersections)
        self.route = []
        self.generate_route()
        self.accumulated_wait = 0

    @staticmethod
    def adjacent(a, b):
        return 0 < abs(a.x - b.x) + abs(a.y - b.y) <= 1

    @staticmethod
    def not_equal(a, b):
        return a.x != b.x or a.y != b.y

    def place_car(self, x=None, y=None):

        if not (x and y):

            # Get city boundaries
            x_min = min(i.x for i in self.traffic_map.intersections)
            x_max = max(i.x for i in self.traffic_map.intersections)
            y_min = min(i.y for i in self.traffic_map.intersections)
            y_max = max(i.y for i in self.traffic_map.intersections)

            # Either x or y should be an integer to be placed on a road
            if random.random() < 0.5:
                x = round(x_min + (x_max - x_min) * random.random(), 2)
                y = random.randint(y_min, y_max)
            else:
                x = random.randint(x_min, x_max)
                y = round(y_min + (y_max - y_min) * random.random(), 2)

        # print(f'Car placed at {(x, y)}')
        return x, y

    def get_next_next(self):
        while True:
            temp = random.choice(self.traffic_map.intersections)
            # Should be adjacent to "next intersection"
            # but not equal to "latest intersection" (no u-turn)
            if self.adjacent(temp, self.route[-1]) and self.not_equal(temp, self.route[-2]):
                self.route.append(temp)
                break

    def generate_route(self):

        # Add "latest intersection" to route
        while True:
            temp = random.choice(self.traffic_map.intersections)
            # Should not be equal but directly adjacent to current position
            if self.not_equal(temp, self) and self.adjacent(temp, self):
                self.route.append(temp)
                break

        # If started at intersection, add current position as "next intersection"
        if self.red_light:
            # Add intersection previous to "latest intersection"
            while True:
                temp = random.choice(self.traffic_map.intersections)
                # Should be adjacent to "latest intersection" but not equal to current position
                if self.adjacent(temp, self.route[-1]) and self.not_equal(temp, self):
                    # NB: add as first element
                    self.route = [temp] + self.route
                    break

            # Add the intersection at the current position
            current_intersection = [i for i in self.traffic_map.intersections if
                                    (i.x, i.y) == (self.x, self.y)][0]
            self.route.append(current_intersection)

        # Else, add random "next intersection" to route
        else:
            while True:
                temp = random.choice(self.traffic_map.intersections)
                # Should be adjacent to current position but not equal to "latest intersection"
                if self.adjacent(temp, self) and self.not_equal(temp, self.route[-1]):
                    self.route.append(temp)
                    break

        # Add "next next intersection" to route
        self.get_next_next()

    def update_position(self, stepsize):

        # Not at an intersection
        if self.route[-2].x == self.x and self.route[-2].y != self.y and not self.red_light:
            self.y += (self.route[-2].y - self.y) / abs(self.route[-2].y - self.y) * stepsize
        elif self.route[-2].x != self.x and self.route[-2].y == self.y and not self.red_light:
            self.x += (self.route[-2].x - self.x) / abs(self.route[-2].x - self.x) * stepsize

        # Reaches an intersection
        if self.route[-2].x == self.x and self.route[-2].y == self.y and not self.red_light:
            # Add next next intersection to route
            self.get_next_next()
            # Set traffic light to True to indicate at intersection
            self.red_light = True

        # Is already at an intersection
        if self.red_light:

            # COMING FROM WEST
            # Turning south
            if self.route[-4].x < self.route[-2].x and self.route[-4].y < self.route[-2].y \
                    and self.route[-4].y == self.route[-3].y:
                # If green light this way
                if self.route[-3].west_south:
                    self.red_light = False
            # Going straight
            if self.route[-4].x < self.route[-2].x and self.route[-4].y == self.route[-2].y:
                # If green light this way
                if self.route[-3].west_east:
                    self.red_light = False
            # Turning north
            if self.route[-4].x < self.route[-2].x and self.route[-4].y > self.route[-2].y \
                    and self.route[-4].y == self.route[-3].y:
                # If green light this way
                if self.route[-3].west_north:
                    self.red_light = False

            # COMING FROM EAST
            # Turning south
            if self.route[-4].x > self.route[-2].x and self.route[-4].y < self.route[-2].y \
                    and self.route[-4].y == self.route[-3].y:
                # If green light this way
                if self.route[-3].east_south:
                    self.red_light = False
            # Going straight
            if self.route[-4].x > self.route[-2].x and self.route[-4].y == self.route[-2].y:
                # If green light this way
                if self.route[-3].east_west:
                    self.red_light = False
            # Turning uo
            if self.route[-4].x > self.route[-2].x and self.route[-4].y > self.route[-2].y \
                    and self.route[-4].y == self.route[-3].y:
                # If green light this way
                if self.route[-3].east_north:
                    self.red_light = False

            # COMING FROM SOUTH
            # Turning west
            if self.route[-4].y > self.route[-2].y and self.route[-4].x > self.route[-2].x \
                    and self.route[-4].x == self.route[-3].x:
                # If green light this way
                if self.route[-3].south_west:
                    self.red_light = False
            # Going straight
            if self.route[-4].y > self.route[-2].y and self.route[-4].x == self.route[-2].x:
                # If green light this way
                if self.route[-3].south_north:
                    self.red_light = False
            # Turning east
            if self.route[-4].y > self.route[-2].y and self.route[-4].x < self.route[-2].x \
                    and self.route[-4].x == self.route[-3].x:
                # If green light this way
                if self.route[-3].south_east:
                    self.red_light = False

            # COMING FROM NORTH
            # Turning east
            if self.route[-4].y < self.route[-2].y and self.route[-4].x < self.route[-2].x \
                    and self.route[-4].x == self.route[-3].x:
                # If green light this way
                if self.route[-3].north_east:
                    self.red_light = False
            # Going straight
            if self.route[-4].y < self.route[-2].y and self.route[-4].x == self.route[-2].x:
                # If green light this way
                if self.route[-3].north_south:
                    self.red_light = False
            # Turning west
            if self.route[-4].y < self.route[-2].y and self.route[-4].x > self.route[-2].x \
                    and self.route[-4].x == self.route[-3].x:
                # If green light this way
                if self.route[-3].north_west:
                    self.red_light = False

            # Add to wait time if stuck at red light
            if self.red_light:
                self.accumulated_wait += 1

        self.x = round(self.x, 2)
        self.y = round(self.y, 2)
        self.route = self.route[-5:]

    def get_predictors(self, v=1):
        if v == 1:
            if self.red_light:
                return [(i.x, i.y) == (self.route[j].x, self.route[j].y) for j in [-4, -3, -2] for
                        i in self.traffic_map.intersections]
            else:
                return [(i.x, i.y) == (self.route[j].x, self.route[j].y) for j in [-3, -2, -1] for
                        i in self.traffic_map.intersections]
        if v == 2:
            if self.red_light:
                return list(sum([(self.route[j].x, self.route[j].y) for j in [-4, -3, -2]], ()))
            else:
                return list(sum([(self.route[j].x, self.route[j].y) for j in [-3, -2, -1]], ()))

        if v == 3:

            # Offset in route if not at red light
            i = 0 if self.red_light else 1

            # Distance to next intersection
            d = abs(self.x - self.route[i-3].x) + abs(self.y - self.route[i-3].y)

            if self.route[i-4].x < self.route[i-2].x and self.route[i-4].y < self.route[i-2].y and \
                    self.route[i-4].y == self.route[i-3].y:
                return self.route[i-3], 0, 'west_south', d
            if self.route[i-4].x < self.route[i-2].x and self.route[i-4].y == self.route[i-2].y:
                return self.route[i-3], 1, 'west_east', d
            if self.route[i-4].x < self.route[i-2].x and self.route[i-4].y > self.route[i-2].y and \
                    self.route[i-4].y == self.route[i-3].y:
                return self.route[i-3], 2, 'west_north', d

            if self.route[i-4].x > self.route[i-2].x and self.route[i-4].y < self.route[i-2].y and \
                    self.route[i-4].y == self.route[i-3].y:
                return self.route[i - 3], 3, 'east_south', d
            if self.route[i-4].x > self.route[i-2].x and self.route[i-4].y == self.route[i-2].y:
                return self.route[i - 3], 4, 'east_west', d
            if self.route[i-4].x > self.route[i-2].x and self.route[i-4].y > self.route[i-2].y and \
                    self.route[i-4].y == self.route[i-3].y:
                return self.route[i - 3], 5, 'east_north', d

            if self.route[i-4].y > self.route[i-2].y and self.route[i-4].x > self.route[i-2].x and \
                    self.route[i-4].x == self.route[i-3].x:
                return self.route[i - 3], 6, 'south_west', d
            if self.route[i-4].y > self.route[i-2].y and self.route[i-4].x == self.route[i-2].x:
                return self.route[i - 3], 7, 'south_north', d
            if self.route[i-4].y > self.route[i-2].y and self.route[i-4].x < self.route[i-2].x and \
                    self.route[i-4].x == self.route[i-3].x:
                return self.route[i - 3], 8, 'south_east', d

            if self.route[i-4].y < self.route[i-2].y and self.route[i-4].x < self.route[i-2].x and \
                    self.route[i-4].x == self.route[i-3].x:
                return self.route[i - 3], 9, 'north_east', d
            if self.route[i-4].y < self.route[i-2].y and self.route[i-4].x == self.route[i-2].x:
                return self.route[i - 3], 10, 'north_south', d
            if self.route[i-4].y < self.route[i-2].y and self.route[i-4].x > self.route[i-2].x and \
                    self.route[i-4].x == self.route[i-3].x:
                return self.route[i - 3], 11, 'north_west', d
