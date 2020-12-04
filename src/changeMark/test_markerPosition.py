import pytest
import numpy

from markerPosition import MarkerPosition 

class TestMarkerPosition(object):
    def setup_method(self, method):
        self.pos = MarkerPosition(2, 2)
    
    def teardown_method(self, method):
        del self.pos
    
    def test_append_and_raise(self):
        with pytest.raises(ValueError):
            self.pos.append(1, '1')

    def test_get_center(self):
        self.pos.append(1, 1)
        self.pos.append(3, 9)
        assert self.pos.get_center() == [2 , 5]
    
    def test_is_near_pos_true(self):
        self.pos.append(1, 1)
        self.pos.append(3, 9)
        assert self.pos.is_near_pos(3, 6)

    def test_is_near_pos_boundary_value_false(self):
        self.pos.append(1, 1)
        self.pos.append(3, 9)
        assert self.pos.is_near_pos(4, 6) == False
