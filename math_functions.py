from math import sqrt

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