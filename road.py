from math_functions import *
from bezier import Bezier, LinearBezier
from parameters import *

class Lane:
    def __init__(self, path, road, beziers, is_key=False, left_lane=None, right_lane=None, lane_width=LANE_WIDTH):
        self.path = path
        self.road = road
        self.beziers = beziers
        self.is_key = is_key

        self.length = sum([bezier.arclength() for bezier in self.beziers])
        self.endpoints = path[0], path[-1]
        self.bezier_paths = [bezier.LUT() for bezier in beziers]
        
        self.left_lane = left_lane
        self.right_lane = right_lane

        self.cars = {}
        self.next_junction = None
        self.prev_junctions = []

        self.last_car = None


class Road:
    def __init__(self, path, n_lanes=3):
        # simulation variables
        self.path = path
        if len(self.path) < 3:
            # cannot do b-spline interp - construct beziers directly
            self.beziers = [LinearBezier(*(np.array(pt) for pt in self.path))]
        else:
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
        self.key_lane = Lane(path=self.path, road=self, beziers=self.beziers, is_key=True)
        self.forward_lanes = [None]
        self.backward_lanes = [None]

        # compute the new lane data
        key_points = path
        key_tans = [bezier.tangent(0) for bezier in self.beziers]
        key_tans.append(self.beziers[-1].tangent(1))
        key_orthonorms = [get_orthonormal_vector(vec=key_tan) for key_tan in key_tans]

        # forward lanes
        for i in range(1, n_lanes+1):
            trans_d = [[k*i*LANE_WIDTH for k in key_orthonorm] for key_orthonorm in key_orthonorms]
            trans_path = [[kx+kdx, ky+kdy] for (kx, ky), (kdx, kdy) in zip(key_points, trans_d)]
            if len(trans_path) < 3:
                # cannot do b-spline interp - construct beziers directly
                trans_beziers = [LinearBezier(*(np.array(pt) for pt in trans_path))]
            else:
                b_splines = cubic_spline_interpolation(trans_path)
                trans_beziers = []
                for P2, Q2, P1, Q1 in zip(b_splines[:-1], b_splines[1:], trans_path[:-1], trans_path[1:]):
                    P2, Q2 = trisect_line_segment(P2, Q2)
                    P1, Q1 = np.array(P1), np.array(Q1)
                    bezier = Bezier(P1, P2, Q2, Q1)
                    trans_beziers.append(bezier)

            # recompute b_spline
            lane = Lane(path=translate_coordinates(
                trans_path,
                self.orthonormal,
                scale=i*LANE_WIDTH), road=self, beziers=trans_beziers, left_lane=self.forward_lanes[-1])
            
            if self.forward_lanes[-1]:
                self.forward_lanes[-1].right_lane = lane
            self.forward_lanes.append(lane)
        
        # backward lanes
        for i in range(1, n_lanes+1):
            trans_d = [[k*i*LANE_WIDTH for k in key_orthonorm] for key_orthonorm in key_orthonorms]
            trans_path = [[kx-kdx, ky-kdy] for (kx, ky), (kdx, kdy) in zip(key_points, trans_d)][::-1]
            if len(trans_path) < 3:
                # cannot do b-spline interp - construct beziers directly
                trans_beziers = [LinearBezier(*(np.array(pt) for pt in trans_path))]
            else:
                b_splines = cubic_spline_interpolation(trans_path)
                trans_beziers = []
                for P2, Q2, P1, Q1 in zip(b_splines[:-1], b_splines[1:], trans_path[:-1], trans_path[1:]):
                    P2, Q2 = trisect_line_segment(P2, Q2)
                    P1, Q1 = np.array(P1), np.array(Q1)
                    bezier = Bezier(P1, P2, Q2, Q1)
                    trans_beziers.append(bezier)

            # recompute b_spline
            lane = Lane(path=translate_coordinates(
                trans_path,
                self.orthonormal,
                scale=i*LANE_WIDTH), road=self, beziers=trans_beziers, left_lane=self.backward_lanes[-1])
            
            if self.backward_lanes[-1]:
                self.backward_lanes[-1].right_lane = lane
            self.backward_lanes.append(lane)
        
        self.forward_lanes.pop(0)
        self.backward_lanes.pop(0)
        
        self.lanes = self.backward_lanes + self.forward_lanes
