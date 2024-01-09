"""
This scenario is a road with a turn lane.
"""

roads = [
    {
        'endpoints': ((100, 500), (490, 500)),
        'n_lanes': 3,
        'is_source': True
    },
    {
        'endpoints': ((520, 500), (900, 500)),
        'n_lanes': 2,
        'is_source': False
    },
    {
        'endpoints': ((500, 480), (500, 100)),
        'n_lanes': 1,
        'is_source': False
    }
]

road_map = [
    '0.0-1.0',
    '0.1-1.1',
    '0.2-2.0'
]