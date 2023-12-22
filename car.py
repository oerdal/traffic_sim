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

        self.lead_car = self.lane.last_car
        self.lane.last_car = self
        self.lane.cars[self.car_id] = self
        if self.lead_car:
            self.lead_car.trail_car = self
        self.trail_car = None

        print(f'Added car with id: {car_id} with a lead car of {self.lead_car} and trail car of {self.trail_car}')

        # drawing init
        self.drawing_init()

    
    def __repr__(self):
        return f'Car #{self.car_id}'
    

    def get_diagnostics(self):
        return self.__dict__


    def drawing_init(self):
        self.unit_vec = self.lane.road.unit_vec
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
    # return (Car, None) if no trailing car and (None, Car) if no leading car and (None, None) if lane empty
    def check_lane_change(self, lane):
        lookahead = self.x + self.l/2 + self.s_0
        lookbehind = self.x - (self.l/2 + self.s_0)

        if not lane.cars:
            return (None, None)

        for car in lane.cars.values():
            front = car.x + car.l/2
            rear = car.x - car.l/2

            # 3 cases:
            # 1) behind the rearmost car
            # 2) in front of the frontmost car
            # 3) between 2 cars

            if lookahead < rear:
                # behind the other car

                if car.trail_car:
                    # there is another car behind us
                    front = car.trail_car.x + car.trail_car.l/2
                    if lookbehind > front:
                        # between cars
                        return (car, car.trail_car)
                    
                    # can't be certain
                    continue
                
                else:
                    # behind the last car in the new lane
                    return (car, None)
                
            elif lookbehind > front:
                # ahead of the other car

                if car.lead_car:
                    # there is another car in front of us
                    # check if we are also clear of the car in front of it
                    rear = car.lead_car.x - car.lead_car.l/2

                    if lookahead < rear:
                        # between cars
                        return (car.lead_car, car)
                    
                    # can't be certain
                    continue

                else:
                    # ahead of the first car in the new lane
                    return (None, car)

        # not enough space   
        return None


    def change_lane(self, direction=None):
        curr_lane = self.lane

        if not direction:
            lanes = [lane for lane in [curr_lane.prev_lane, curr_lane.next_lane] if lane]
            lane = random.choice(lanes) if lanes else None
        else:
            # car wishes to change to a specific lane
            if direction == 'L' and lane.prev_lane:
                lane = lane.prev_lane
            elif direction == 'R' and lane.next_lane:
                lane = lane.next_lane
            else:
                logging.warning(f'Invalid lane change direction {direction}.')
                lane = None
        
        if not lane:
            # no available lane to move into
            return False

        print(f'Car {self.car_id} wishes to change lanes into lane {lane}.')

        can_change = self.check_lane_change(lane)

        if can_change:
            print(f'Car {self.car_id} changing lanes from {curr_lane} into lane {lane}.')
            # do lane change
            lead, trail = can_change

            print(f'Lead car: {lead} and trail car: {trail}.')

            ## Update the old lane and cars
            if not(self.lead_car or self.trail_car):
                # we are the only car
                curr_lane.last_car = None
            else:
                # there is at least 1 other car in the old lane
                if self.lead_car:
                    if self.trail_car:
                        # we are a central car
                        self.lead_car.trail_car = self.trail_car
                        self.trail_car.lead_car = self.lead_car
                    else:
                        # we are the rearmost car
                        self.lead_car.trail_car = None
                        curr_lane.last_car = self.lead_car

                else:
                    if self.trail_car:
                        # we are the frontmost car
                        self.trail_car.lead_car = None
            del curr_lane.cars[self.car_id]

            ## Update the new lane and cars
            if not(lead or trail):
                # moving into an empty lane
                lane.last_car = self
            else:
                # there is at least one other car in the new lane
                if lead:
                    if trail:
                        # moving in between two cars
                        lead.trail_car = self
                        trail.lead_car = self
                        self.lead_car = lead
                        self.trail_car = trail
                    
                    else:
                        # moving to the back of all other cars
                        lead.trail_car = self
                        self.lead_car = lead
                        self.trail_car = None
                        lane.last_car = self
                
                else:
                    if trail:
                        # moving the front of all other cars
                        trail.lead_car = self
                        self.lead_car = None
                        self.trail_car = trail
            
            lane.cars[self.car_id] = self
            self.lane = lane
            
            print(f'lead car: {self.lead_car} - ({self.lead_car.lead_car if self.lead_car else None}, {self.lead_car.trail_car if self.lead_car else None})')
            print(f'car: {self} - ({self.lead_car}, {self.trail_car})')
            print(f'trail car: {self.trail_car} - ({self.trail_car.lead_car if self.trail_car else None}, {self.trail_car.trail_car if self.trail_car else None})')
            
            print('===')
            print(lane.cars)
            print('===')

            self.drawing_init()

        else:
            # don't change lanes
            print('Couldn\'t change lanes')
            

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