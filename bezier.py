import numpy as np

class Bezier:
    def __init__(self, P0, P1, P2, P3):
        self.P0 = P0
        self.P1 = P1
        self.P2 = P2
        self.P3 = P3

        self.LUT_cache = None
    

    def __repr__(self):
        return f'PO: {self.P0}, P1: {self.P1}, P2: {self.P2}, P3: {self.P3}'


    def interpolate(self, t):
        t2 = t*t
        t3 = t2*t
        a = (1 + 3*(t2 - t) - t3) * self.P0
        b = 3*(t -2*t2 + t3) * self.P1
        c = 3*(t2 - t3) * self.P2
        d = t3 * self.P3
        return a + b + c + d
    
    
    def LUT(self, n=100):
        """
        Compute and cache a look-up table (LUT) with n evenly-spaced t-values
        """
        if self.LUT_cache and len(self.LUT) == n:
            # already computed
            ...
        else:
            # need to recompute
            ts = np.linspace(0, 1, n)
            self.LUT_cache = [self.interpolate(t) for t in ts]

        return self.LUT_cache
    

    def tangent(self, t):
        a = 3*(1-t)*(1-t) * (self.P1-self.P0)
        b = 6*t*(1-t) * (self.P2-self.P1)
        c = 3*t*t * (self.P3-self.P2)
        return a + b + c
        return 3*(1-t)**2 * (self.P1-self.P0) + 6*t*(1-t) * (self.P2-self.P1) + 3*t**2 * (self.P3-self.P2)
