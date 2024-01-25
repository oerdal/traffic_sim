from math_functions import *
from bezier import Bezier
from parameters import *

class Lane:
    def __init__(self, path, road, beziers, left_lane=None, right_lane=None, lane_width=LANE_WIDTH):
        self.cars = {}
        self.path = path
        self.endpoints = path[0], path[-1]
        self.length = magnitude(self.endpoints)
        self.road = road
        self.beziers = beziers
        self.bezier_paths = [bezier.LUT() for bezier in beziers]
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
            P1, Q1 = np.array(P1), np.array(Q1)
            bezier = Bezier(P1, P2, Q2, Q1)
            self.beziers.append(bezier)
            
        self.endpoints = path[0], path[-1]
        self.n_lanes = n_lanes

        # math initialization
        self.unit_vec = get_unit_vec(self.endpoints)
        self.orthonormal = get_orthonormal_vector(vec=self.unit_vec)

        # linkage to other classes
        self.key_lane = Lane(path=self.path, road=self, beziers=self.beziers)
        self.lanes = [self.key_lane]

        if n_lanes > 1:
            pass
            # compute the new lane data
            key_points = path
            key_tans = [bezier_tangent(P0, P1, P2, P3, 0) for P0, P1, P2, P3 in self.beziers]
            key_tans.append(bezier_tangent(*self.beziers[-1], 1))
            key_orthonorms = [get_orthonormal_vector(vec=key_tan) for key_tan in key_tans]

            for i in range(1, n_lanes):
                trans_d = [[k*i*LANE_WIDTH for k in key_orthonorm] for key_orthonorm in key_orthonorms]
                trans_path = [[kx+kdx, ky+kdy] for (kx, ky), (kdx, kdy) in zip(key_points, trans_d)]
                b_splines = cubic_spline_interpolation(trans_path)
                trans_beziers = []
                for P2, Q2, P1, Q1 in zip(b_splines[:-1], b_splines[1:], trans_path[:-1], trans_path[1:]):
                    P2, Q2 = trisect_line_segment(P2, Q2)
                    bezier_control = np.stack((P1, P2, Q2, Q1))
                    trans_beziers.append(bezier_control)

                # recompute b_spline
                lane = Lane(path=translate_coordinates(
                    trans_path,
                    self.orthonormal,
                    scale=i*LANE_WIDTH), road=self, beziers=trans_beziers, left_lane=self.lanes[-1])
                self.lanes[-1].right_lane = lane
                self.lanes.append(lane)
    
