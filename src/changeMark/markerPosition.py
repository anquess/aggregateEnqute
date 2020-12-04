import numpy

class MarkerPosition(object):
    def __init__(self, w, h):
        self.position_list = []
        self.w = w
        self.h = h

    def append(self, x, y):
        if type(x) is not int or type(y) is not int:
            raise ValueError
        self.position_list.append([x, y])

    def is_near_pos(self, x, y) -> bool:
        if type(x) is not int or type(y) is not int:
            raise ValueError
        center_x , center_y = self.get_center()
        return abs(center_x - x) < self.w and abs(center_y - y) < self.h

    def get_center(self) -> list:
        return numpy.mean(self.position_list, axis=0).tolist()