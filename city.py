import random
import numpy as np
import tkinter
from PIL import Image, ImageTk
from car import Car
from intersection import Intersection


class City(object):

    def __init__(self, stepsize=0.01):
        self.intersections = []
        self.intersections.append(Intersection(1, 1, static_open=True))
        self.intersections.append(Intersection(1, 2, static_open=True))
        self.intersections.append(Intersection(1, 3, static_open=True))
        self.intersections.append(Intersection(2, 1, static_open=True))
        self.intersections.append(Intersection(2, 2))
        self.intersections.append(Intersection(2, 3, static_open=True))
        self.intersections.append(Intersection(3, 1, static_open=True))
        self.intersections.append(Intersection(3, 2, static_open=True))
        self.intersections.append(Intersection(3, 3, static_open=True))
        self.cars = []
        self.stepsize = stepsize
        self.total_wait_time = 0

        # Set up window
        self.labels = []
        self.tk = tkinter.Tk()
        self.tk.title('TrafficMap')
        self.tk.wm_attributes("-topmost", 1)
        self.tk.wm_geometry("%dx%d%+d%+d" % (500, 500, 0, 0))

    def update_positions(self, visualize=False):
        for i, c in enumerate(self.cars):
            c.update_position(stepsize=self.stepsize)

            # Draw on map
            if visualize:
                square_im = ImageTk.PhotoImage(Image.new('RGB', (3, 3)))
                temp_label = tkinter.Label(name='car_{}'.format(i), image=square_im,
                                           compound=tkinter.NONE)
                temp_label.image = square_im
                temp_label.place(x=100 * c.x, y=100 * c.y, anchor=tkinter.CENTER)
                self.labels.append(temp_label)

    def build_window(self):
        # Add roads
        for i in self.intersections:
            for j in self.intersections:
                if (i.x == j.x and not i.y == j.y) or (not i.x == j.x and i.y == j.y):
                    x_len = max(1, 100 * abs(i.x-j.x))
                    y_len = max(1, 100 * abs(i.y-j.y))
                    temp_line_im = ImageTk.PhotoImage(Image.new('RGB', (x_len, y_len)))
                    temp_label = tkinter.Label(name=f'road_({i.x}_{i.y})-({j.x}_{j.y})',
                                               image=temp_line_im, compound=tkinter.NONE)
                    temp_label.image = temp_line_im
                    mid_x = 100 * (min(i.x, j.x) + abs(i.x - j.x)/2)
                    mid_y = 100 * (min(i.y, j.y) + abs(i.y - j.y)/2)
                    temp_label.place(x=mid_x, y=mid_y, anchor=tkinter.CENTER)
                    self.labels.append(temp_label)

        # Add intersections
        square_im = ImageTk.PhotoImage(Image.new('RGB', (10, 10)))
        for i in self.intersections:
            temp_label = tkinter.Label(name=f'intersection_{i.x}_{i.y}',
                                       image=square_im, compound=tkinter.NONE)
            temp_label.image = square_im
            temp_label.place(x=100*i.x, y=100*i.y, anchor=tkinter.CENTER)
            self.labels.append(temp_label)

    def sum_wait_time(self):
        self.total_wait_time = 0
        for i, c in enumerate(self.cars):
            self.total_wait_time += c.accumulated_wait
        return self.total_wait_time

    def place_cars(self, n=1, clear=False):
        if clear:
            self.cars = []
        for _ in range(n):
            self.cars.append(Car(self))

    def get_predictors(self, v=3):
        if v == 1 or v == 2:
            return [c.get_predictors(v=v) for c in self.cars]
        if v == 3:
            feature_vector = [0 for _ in range(12 * len(self.intersections))]
            for c in self.cars:
                temp_feature = c.get_predictors(v=3)
                next_intersection = np.argmax([temp_feature[0] == i for i in self.intersections])
                feature_vector[12 * next_intersection + temp_feature[1]] += (1 - temp_feature[3])
            return feature_vector


if __name__ == '__main__':
    city = City(stepsize=0.01)
    city.build_window()
    city.place_cars(n=10)
    while True:
        if random.random() < 0.01:
            city.intersections[4].change_state()
        city.sum_wait_time()
        city.update_positions(visualize=True)
        city.get_predictors(v=3)
        city.tk.update_idletasks()
        city.tk.update()
