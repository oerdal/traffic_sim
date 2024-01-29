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
        self.beziers = self.compute_beziers(path)
            
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
            
            self.build_lane(trans_path, self.forward_lanes, i)
        
        # backward lanes
        for i in range(1, n_lanes+1):
            trans_d = [[k*i*LANE_WIDTH for k in key_orthonorm] for key_orthonorm in key_orthonorms]
            trans_path = [[kx-kdx, ky-kdy] for (kx, ky), (kdx, kdy) in zip(key_points, trans_d)][::-1]
            
            self.build_lane(trans_path, self.backward_lanes, i)
        
        self.forward_lanes.pop(0)
        self.backward_lanes.pop(0)
        
        self.lanes = self.backward_lanes + self.forward_lanes

    
    def build_lane(self, path, lanes, lane_idx):
        beziers = self.compute_beziers(path)

        # recompute b_spline
        lane = Lane(path=translate_coordinates(path, self.orthonormal, scale=lane_idx*LANE_WIDTH),
                    road=self,
                    beziers=beziers,
                    left_lane=lanes[-1])
        
        if lanes[-1]:
            lanes[-1].right_lane = lane
        lanes.append(lane)

        return lanes


    def compute_beziers(self, path):
        if len(path) < 3:
            # cannot do b-spline interp - construct beziers directly
            beziers = [LinearBezier(*(np.array(pt) for pt in path))]
        else:
            b_splines = cubic_spline_interpolation(path)
            beziers = []
            for P2, Q2, P1, Q1 in zip(b_splines[:-1], b_splines[1:], path[:-1], path[1:]):
                P2, Q2 = trisect_line_segment(P2, Q2)
                P1, Q1 = np.array(P1), np.array(Q1)
                bezier = Bezier(P1, P2, Q2, Q1)
                beziers.append(bezier)
        
        return beziers