from scipy.interpolate import interp1d
import random
from math import sqrt
from parameters import *

import logging

class Car:
    def __init__(self, car_args, car_id, lane):
        # variables for the intelligent driver model

        # currently all the distances and speeds are in pixels and pixels/frame
        # let 2 pixel = 1 meter
        self.dt = 1/60 # 1/60th of a second = spf
        self.ppm = 2

        self.__dict__.update(**car_args)

        self.v_0 = self.v_0*self.ppm*self.dt # desired velocity (pixels/second)
        self.T = self.T/self.dt # desired time headway (min time to vehicle ahead)
        self.b = self.b*self.ppm*(self.dt**2) # max deceleration (comfortable)
        self.a = self.a*self.ppm*(self.dt**2)
        self.v = self.v*self.v_0 # cars start at half the desired velocity
        # IF THIS NUMBER IS TOO LOW OR b IS TOO LOW, CARS WILL COLLIDE WHICH CURRENTLY CAUSES
        # ISSUES WITH DISAPPEARING VEHICLES 
        self.s_0 = self.s_0*self.ppm # minimum spacing (gap between car ahead)
        self.l = self.l*self.ppm

        # initialization
        self.x = 0
        self.max_v = 1.2*self.v_0
        self.min_v = 0

        # simulation init
        self.car_id = car_id
        self.lane = lane
        self.unit_vec = self.lane.road.unit_vec
        
        lead_cars = list(self.lane.cars.values())
        self.lead_car = lead_cars[-1] if lead_cars else None
        if self.lead_car:
            self.lead_car.trail_car = self
        self.trail_car = None

        (x1, y1), (x2, y2) = self.lane.endpoints

        self.xpos = interp1d((0.0, 1.0), (x1, x2))
        self.ypos = interp1d((0.0, 1.0), (y1, y2))
    

    def compute_pos(self):
        # we can consider x to represent the proportion of the road through
        # which the car has progressed and use interpolation to compute the
        # coordinates/position of the car relative to the entire simulation
        return (self.xpos(self.x/self.lane.length), self.ypos(self.x/self.lane.length))
    

    # return a tuple of the new lead and trail car if the lane is changed into
    # return None if no lane change is possible
    # return (Car, None) if no trailing car and (None, Car) if no leading car
    def check_lane_change(self, lane):
        lookahead = self.x + self.l/2 + self.s_0
        lookbehind = self.x - (self./2 + self.s_0)

        for car in lane:
            front, rear = car.x + car.l/2, car.x - car.l/2

            if (lookahead >= rear and lookahead <= front) or (lookbehind >= rear and lookbehind <= front):
                # invalid lane change location
                return False
        
        return True


    def change_lane(self, direction=None):
        curr_lane = self.lane

        if not direction:
            lanes = [lane for lane in [curr_lane.prev, curr_lane.next] if lane]
            lane = random.choice(lanes) if lanes else None
        else:
            # car wishes to change to a specific lane
            if direction == 'L' and lane.prev:
                lane = lane.prev
            elif direction == 'R' and lane.next:
                lane = lane.prev
            else:
                logging.warning(f'Invalid lane change direction {direction}.')
                lane = None
        
        if not lane:
            # no available lane to move into
            return False

        print(f'Car {self.car_id} wishes to change lanes into lane {lane}.')

        can_change = self.validate_lane_change(lane)
        if can_change:
            # do lane change
            ...

        else:
            # don't change lanes
            ...

        return can_change




    def update(self):
        # check if there is a leading car
        if self.lead_car:
            # standard IDM model
            delta_v = self.lead_car.v - self.v
            s_star = self.s_0 + max(0, self.v*self.T + (self.v*delta_v)/(2*sqrt(self.a*self.b)))
            s = self.lead_car.x - self.x
            dv = self.a*(1 - (self.v/self.v_0)**self.delta - (s_star/s)**2) if s != 0 else 0
            # print(f'Car {self.car_id} || delta_v: {delta_v} || s_star: {s_star} || s: {s} || v: {self.v}')
        else:
            # free road only
            dv = self.a*(1 - (self.v/self.v_0)**self.delta)
            # print(self.a, self.v, self.v_0, dv)
            
        dt = 1
        v = self.v + dv*dt
        x = self.x + self.v * dt + 0.5 * dv * dt * dt

        self.v = max(self.min_v, min(self.max_v, v))
        self.x = max(0, x)


        return self.x < self.lane.length


class CarGenerator:
    @staticmethod
    def generate_car(random_init=True):
        if random_init:
            car_args = {
                'v_0': random.gauss(V_0_MU, 1),
                'T': random.gauss(T_MU, 0.5),
                'b': random.gauss(B_MU, 1),
                'a': random.gauss(A_MU, 0.5),
                'v': random.gauss(V_MU, 0.1),
                's_0': random.gauss(S_0_MU, 0.5),
                'l': random.gauss(L_MU, 0.5),
                'delta': random.gauss(DELTA_MU, 0.5)
            }

        else:
            car_args = {
                'v_0': V_0_MU,
                'T': T_MU,
                'b': B_MU,
                'a': A_MU,
                'v': V_MU,
                's_0': S_0_MU,
                'l': L_MU,
                'delta': DELTA_MU
            }
        
        return car_args