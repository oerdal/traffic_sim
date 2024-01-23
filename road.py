from math_functions import *
from parameters import *

class Lane:
    def __init__(self, path, road, beziers, left_lane=None, right_lane=None, lane_width=LANE_WIDTH):
        self.cars = {}
        self.path = path
        self.endpoints = path[0], path[-1]
        self.length = magnitude(self.endpoints)
        self.road = road
        self.beziers = beziers
        self.bezier_paths = [bezier_curve(P0, P1, P2, P3) for P0, P1, P2, P3 in beziers]
        self.length*=len(self.bezier_paths)
        self.left_lane = left_lane
        self.right_lane = right_lane

        self.next_junction = None
        self.prev_junctions = []

        self.last_car = None


class Road:
    def __init__(self, path, n_lanes=3):
        # simulation variables
        self.path = path
        b_splines = cubic_spline_interpolation(self.path)
        self.beziers = []
        for P2, Q2, P1, Q1 in zip(b_splines[:-1], b_splines[1:], self.path[:-1], self.path[1:]):
            P2, Q2 = trisect_line_segment(P2, Q2)
            bezier_control = np.stack((P1, P2, Q2, Q1))
            self.beziers.append(bezier_control)
            
        self.endpoints = path[0], path[-1]
        self.n_lanes = n_lanes

        # math initialization
        self.unit_vec = get_unit_vec(self.endpoints)
        self.orthonormal = get_orthonormal_vector(vec=self.unit_vec)

        # linkage to other classes
        self.key_lane = Lane(path=self.path, road=self, beziers=self.beziers)
        self.lanes = [self.key_lane]

        for i in range(1, n_lanes):
            lane = Lane(path=translate_coordinates(
                self.key_lane.path,
                self.orthonormal,
                scale=i*LANE_WIDTH), road=self, beziers=self.beziers, left_lane=self.lanes[-1])
            self.lanes[-1].right_lane = lane
            self.lanes.append(lane)
    
