import numpy

class MarkerPosition(object):
    def __init__(self, w, h, x, y):
        if self.is_args_in_type_error(w, h, x, y):
            raise ValueError
        self.position_list = []
        self.w = w
        self.h = h
        self.append(x, y)

    def append(self, x, y):
        if self.is_args_in_type_error(x, y):
            raise ValueError
        self.position_list.append([x, y])

    def is_near_pos(self, x, y) -> bool:
        if self.is_args_in_type_error(x, y):
            raise ValueError
        center_x , center_y = self.get_center()
        return abs(center_x - x) < self.w and abs(center_y - y) < self.h

    def get_center(self) -> list:
        average_pos = numpy.mean(self.position_list, axis=0)
        center_pos = [ pos.astype(numpy.int32) for pos in average_pos ] 
        return center_pos

    def is_args_in_type_error(self, *args) -> bool:
        for arg in args:
            if type(arg) is not int and type(arg) is not numpy.int64:
                return True
        return False
