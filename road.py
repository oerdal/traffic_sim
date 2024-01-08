from math_functions import *
from parameters import *

class Lane:
    def __init__(self, endpoints, road, left_lane=None, right_lane=None, lane_width=LANE_WIDTH):
        self.cars = {}
        self.endpoints = endpoints
        self.length = magnitude(endpoints)
        self.road = road
        self.left_lane = left_lane
        self.right_lane = right_lane

        self.last_car = None


class Road:
    def __init__(self, endpoints, junction_pos=0, n_lanes=3):
        # simulation variables
        self.endpoints = endpoints
        self.n_lanes = n_lanes

        # math initialization
        self.unit_vec = get_unit_vec(endpoints)
        self.orthonormal = get_orthonormal_vector(vec=self.unit_vec)

        # linkage to other classes
        self.key_lane = Lane(endpoints=endpoints, road=self)
        self.lanes = [self.key_lane]

        self.next_junction = None
        self.prev_junction = None
        self.junction_pos = junction_pos

        for i in range(1, n_lanes):
            lane = Lane(endpoints=translate_coordinates(
                self.key_lane.endpoints,
                self.orthonormal,
                scale=i*LANE_WIDTH), road=self, left_lane=self.lanes[-1])
            self.lanes[-1].right_lane = lane
            self.lanes.append(lane)
    
