import random


class Intersection(object):

    def __init__(self, x, y, static_open=False):
        self.state = None
        self.x = x
        self.y = y
        self.static_open = static_open
        if self.static_open:
            self.west_north = True
            self.west_east = True
            self.west_south = True
            self.south_west = True
            self.south_north = True
            self.south_east = True
            self.east_south = True
            self.east_west = True
            self.east_north = True
            self.north_east = True
            self.north_south = True
            self.north_west = True
        else:
            self.change_state()

    def change_state(self, state=None, verbose=False):

        if not self.static_open:

            if state is None:
                self.state = random.randrange(4)
                if verbose:
                    print('state_{}'.format(self.state))
            else:
                self.state = state

            if self.state == 0:
                self.west_north = False
                self.west_east = True
                self.west_south = True

                self.south_west = False
                self.south_north = False
                self.south_east = True

                self.east_south = False
                self.east_west = True
                self.east_north = True

                self.north_east = False
                self.north_south = False
                self.north_west = True

            elif self.state == 1:
                self.west_north = False
                self.west_east = False
                self.west_south = True

                self.south_west = False
                self.south_north = True
                self.south_east = True

                self.east_south = False
                self.east_west = False
                self.east_north = True

                self.north_east = False
                self.north_south = True
                self.north_west = True

            elif self.state == 2:
                self.west_north = True
                self.west_east = False
                self.west_south = True

                self.south_west = False
                self.south_north = False
                self.south_east = True

                self.east_south = True
                self.east_west = False
                self.east_north = True

                self.north_east = False
                self.north_south = False
                self.north_west = True

            elif self.state == 3:
                self.west_north = False
                self.west_east = False
                self.west_south = True

                self.south_west = True
                self.south_north = False
                self.south_east = True

                self.east_south = False
                self.east_west = False
                self.east_north = True

                self.north_east = True
                self.north_south = False
                self.north_west = True

    def get_incoming(self, cars):
        position = (-1, -1)
        try:
            for c in cars:
                if c.route[-1].x == self.x and c.route[-1].y == self.y:
                    position = (c.x, c.y)
        except IndexError:
            print('IndexError')
            pass
        return position
