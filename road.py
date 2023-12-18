from math_functions import *
from parameters import *

class Lane:
    def __init__(self, endpoints, lane_width=LANE_WIDTH):
        self.cars = []
        self.endpoints = endpoints
        self.length = magnitude(endpoints)


class Road:
    def __init__(self, endpoints, n_lanes=3):
        self.endpoints = endpoints
        self.n_lanes = n_lanes

        self.unit_vec = get_orthonormal_vector(endpoints=self.endpoints)

        self.key_lane = Lane(endpoints)
        self.lanes = [self.key_lane]

        for i in range(1, n_lanes):
            self.lanes.append(Lane(translate_coordinates(
                self.key_lane.endpoints,
                self.unit_vec,
                scale=i*LANE_WIDTH)))
    
