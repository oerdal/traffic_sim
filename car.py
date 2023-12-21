from scipy.interpolate import interp1d
import random
from math import sqrt

class Car:
    def __init__(self, car_id, lane):
        # variables for the intelligent driver model
        self.v_0 = 3 # desired velocity
        self.T = 1 # desired time headway (min time to vehicle ahead)
        self.max_a = 0.73 # max acceleration
        self.b = 0.2 # max deceleration (comfortable)
        self.max_v = 3
        self.min_v = -1

        self.delta = random.choice([2, 3, 4, 5, 6])

        self.s_0 = 0.005 # minimum spacing (gap between car ahead)
        self.l = 10


        self.a = 0.05
        self.v = 0
        self.x = 0


        # simulation variables
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
            
        dt = 1
        v = self.v + dv*dt
        x = self.x + self.v * dt + 0.5 * dv * dt * dt

        self.v = max(self.min_v, min(self.max_v, v))
        self.x = max(0, x)


        return self.x < self.lane.length