class Car:
    def __init__(self):
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