import numpy as np
from parameters import C_VALUES, T_VALUES
from math_functions import magnitude

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
        """
        Compute the value of the Bezier fucntion at the specified t in [0,1]
        """
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
        """
        Compute the derivative of the Bezier function at the specified t in [0,1]
        """
        a = 3*(1-t)*(1-t) * (self.P1-self.P0)
        b = 6*t*(1-t) * (self.P2-self.P1)
        c = 3*t*t * (self.P3-self.P2)
        return a + b + c
        return 3*(1-t)**2 * (self.P1-self.P0) + 6*t*(1-t) * (self.P2-self.P1) + 3*t**2 * (self.P3-self.P2)


    def arclength(self):
        """
        Utilize Gaussian Quadrature with change of limits from [-1,1] to [0,1]
        https://www.youtube.com/watch?v=Uf3l3hMZecA
        """
        n = len(T_VALUES)

        cum_len = 0
        for c, t in zip(C_VALUES, T_VALUES):
            t = 0.5 * t + 0.5
            l = magnitude(vec=self.tangent(t))
            cum_len += c * l
        
        return 0.5 * cum_len


class LinearBezier:
    def __init__(self, P0, P1):
        self.P0 = P0
        self.P1 = P1

        self.LUT_cache = None
    

    def __repr__(self):
        return f'PO: {self.P0}, P1: {self.P1}'


    def interpolate(self, t):
        """
        Compute the value of the Bezier fucntion at the specified t in [0,1]
        """
        return (1 - t) * self.P0 + t * self.P1
    
    
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
        """
        Compute the derivative of the Bezier function at the specified t in [0,1]
        """
        return self.P1 - self.P0


    def arclength(self):
        """
        Utilize Gaussian Quadrature with change of limits from [-1,1] to [0,1]
        https://www.youtube.com/watch?v=Uf3l3hMZecA
        """
        return magnitude(endpoints=(self.P0, self.P1))