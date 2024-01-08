from road import Road

class Junction:
    def __init__(self, lane_map):
        """
        Initialize the junction to be a connector to the passed list of roads.
        """
        self.lane_map = lane_map

    # we must define some level of "lane connectivity" for the junction.
    # this will allow us to move cars across the junction.
    # ex: right 2 lanes of road x feed into right 2 lanes of road y and
    # left 2 lanes of road x feed into the left 2 lanes of road z.

class TwoWayJunction(Junction):
    ...



class StopJunction(Junction):
    ...