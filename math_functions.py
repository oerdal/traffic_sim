from math import sqrt

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

# coords: the coordinates to translate
# vec: the translation vector (should be a unit vector)
# scale: how much to scale the unit vector
def translate_coordinates(coords, vec, scale=1):
    tvec = tuple(v*scale for v in vec)

    new_coords = tuple(tuple(a+v for a, v in zip(tvec, coord)) for coord in coords)
    
    return new_coords