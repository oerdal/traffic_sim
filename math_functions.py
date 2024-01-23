from math import sqrt
import numpy as np

def get_unit_vec(endpoints):
    if endpoints:
        (x1, y1), (x2, y2) = endpoints
        v1, v2 = x2-x1, y2-y1

        mag = sqrt(v1**2 + v2**2)

        return (v1/mag, v2/mag)



# pass tuple of endpoints or a single displacement vector
# currently works with 2D space coordinate space only
def get_orthonormal_vector(endpoints=None, vec=None):
    if endpoints:
        (x1, y1), (x2, y2) = endpoints
        v1, v2 = x2-x1, y2-y1

        o1, o2 =  (v2, -v1) if v1 >= 0 else (-v2, v1)
        mag = sqrt(o1**2 + o2**2)

        return (o1/mag, o2/mag)
    
    elif vec:
        v1, v2 = vec

        o1, o2 =  (v2, -v1) if v1 >= 0 else (-v2, v1)
        mag = sqrt(o1**2 + o2**2)

        return (o1/mag, o2/mag)

    return None


def magnitude(endpoints):
    (x1, y1), (x2, y2) = endpoints

    return sqrt((x2-x1)**2 + (y2-y1)**2)


# coords: the coordinates to translate
# vec: the translation vector (should be a unit vector)
# scale: how much to scale the unit vector
def translate_coordinates(coords, vec, scale=1):
    tvec = tuple(v*scale for v in vec)

    new_coords = tuple(tuple(a+v for a, v in zip(tvec, coord)) for coord in coords)
    
    return new_coords
    

def make_141_matrix(n):
    dim = n-2

    M = np.zeros((dim, dim))
    M += np.diag(np.full(dim, 4))
    M += np.diag(np.ones(dim-1), 1)
    M += np.diag(np.ones(dim-1), -1)

    return M


def make_spline_const_matrix(path):
    x, y = [list(p) for p in zip(*path)] # unzip list of tuples

    m = len(path)-2

    C = np.zeros((2, m)) # transpose later

    Cx = [6*v for v in x[1:-1]]
    Cy = [6*v for v in y[1:-1]]

    # set the 4 edge values
    Cx[0] -= x[0]
    Cx[-1] -= x[-1]
    Cy[0] -= y[0]
    Cy[-1] -= y[-1]

    C = np.array([Cx, Cy]).T

    return C


def cubic_spline_interpolation(path):
    # S_i = 1/6 B_{i-1} + 2/3 B_i + 1/6 B_{i+1}
    # where S_i is point i of the path
    M = make_141_matrix(len(path))
    M_inv = np.linalg.inv(M)

    C = make_spline_const_matrix(path)

    B_star = np.matmul(M_inv, C)

    # add the edge points S_0 and S_n
    B_star = np.concatenate((np.array([path[0]]), B_star, np.array([path[-1]])))

    return B_star


def trisect_line_segment(B0, B1):
    B10 = (B1 - B0)/3
    
    return B0+B10, B1-B10
    

def bezier_interpolation(P0, P1, P2, P3, t):
    return (1-t)**3 * P0 + 3*t*(1-t)**2 * P1 + 3*t**2 *(1-t) * P2 + t**3 * P3


def bezier_curve(P0, P1, P2, P3, n=100):
    ts = np.linspace(0, 1, n)

    return [bezier_interpolation(P0, P1, P2, P3, t) for t in ts]


def bezier_tangent(P0, P1, P2, P3):
    ...