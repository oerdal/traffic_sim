from math_functions import *
from parameters import *

class Lane:
    def __init__(self, endpoints, road, lane_width=LANE_WIDTH):
        self.cars = []
        self.endpoints = endpoints
        self.length = magnitude(endpoints)
        self.road = road


class Road:
    def __init__(self, endpoints, n_lanes=3):
        self.endpoints = endpoints
        self.n_lanes = n_lanes

        self.unit_vec = get_unit_vec(endpoints)
        self.orthonormal = get_orthonormal_vector(vec=self.unit_vec)

        self.key_lane = Lane(endpoints, self)
        self.lanes = [self.key_lane]

        for i in range(1, n_lanes):
            self.lanes.append(Lane(translate_coordinates(
                self.key_lane.endpoints,
                self.orthonormal,
                scale=i*LANE_WIDTH), self))
    
