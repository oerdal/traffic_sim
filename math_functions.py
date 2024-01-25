from math import sqrt
import numpy as np

def get_unit_vec(endpoints):
    v1, v2 = endpoints
    if not (isinstance(v1, float) and isinstance(v2, float)):
        (x1, y1), (x2, y2) = v1, v2
        v1, v2 = x2-x1, y2-y1

    mag = sqrt(v1**2 + v2**2)

    return (v1/mag, v2/mag)


def get_normal_vector(vec):
    v1, v2 = vec

    return (-v2, v1)


# pass tuple of endpoints or a single displacement vector
# currently works with 2D space coordinate space only
def get_orthonormal_vector(endpoints=None, vec=None):
    if endpoints:
        (x1, y1), (x2, y2) = endpoints
        v1, v2 = x2-x1, y2-y1

        # o1, o2 =  (v2, -v1) if v1 >= 0 else (-v2, v1)
        o1, o2 = -v2, v1
        mag = sqrt(o1**2 + o2**2)

        return (o1/mag, o2/mag)
    
    elif isinstance(vec, np.ndarray):
        v1, v2 = vec
        o1, o2 = -v2, v1
        
        mag = sqrt(o1**2 + o2**2)
        return [o1/mag, o2/mag]

    elif vec:
        v1, v2 = vec

        # o1, o2 =  (v2, -v1) if v1 >= 0 else (-v2, v1)
        o1, o2 = -v2, v1
        mag = sqrt(o1**2 + o2**2)

        return (o1/mag, o2/mag)

    return None


def magnitude(endpoints=None, vec=None):
    if not endpoints:
        v1, v2 = vec
        return sqrt(v1*v1 + v2*v2)

    (x1, y1), (x2, y2) = endpoints
    v1, v2 = x2-x1, y2-y1

    return sqrt(v1*v1 + v2*v2)


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
    