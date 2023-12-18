from scipy.interpolate import interp1d

class Car:
    def __init__(self, lane):
        # variables for the intelligent driver model
        self.v_0 = 30
        self.T = 1.5
        self.max_a = 0.73
        self.max_b = 1.67
        self.max_v = 3
        self.delta = 4
        self.s_0 = 2
        self.l = 10


        self.a = 0.1
        self.v = 0
        self.x = 0


        self.lane = lane
        (x1, y1), (x2, y2) = self.lane.endpoints

        self.xpos = interp1d((0.0, 1.0), (x1, x2))
        self.ypos = interp1d((0.0, 1.0), (y1, y2))
    

    def compute_pos(self):
        # we can consider x to represent the proportion of the road through
        # which the car has progressed and use interpolation to compute the
        # coordinates/position of the car relative to the entire simulation
        return (self.xpos(self.x/self.lane.length), self.ypos(self.x/self.lane.length))


    def update(self):
        # x_{n+1} = x_n + v_n \delta t + 1/2 a_n \delta t^2
        # v_{n+1} = v_n + 1/2 (a_n + a_{n+1}) \delta t
        delta = 1

        a = self.a
        v = self.v + 0.5 * (self.a + a) * delta
        x = self.x + self.v * delta + 0.5 * self.a * delta * delta

        self.a = a
        self.v = v if v < self.max_v else self.max_v
        self.x = x

        return self.x < self.lane.length