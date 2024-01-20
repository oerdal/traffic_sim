import dearpygui.dearpygui as dpg

from car import Car, CarGenerator
from road import Road
from junction import Junction
from parameters import *

import logging
import random

class Simulation:
    def __init__(self, scenario=None, sim_len=50):
        self.cars = {}
        self.roads = []
        self.road_ends = []
        self.junctions = []
        self.dead_cars = []
        self.fps = 60
        self.ticks_since_car = 0
        self.ticks_since_lane_change = 0

        # autoincrement ids for retreival
        self.car_id = 0
        # self.road_id = 0

        self.focused_car = None

        self.scenario = scenario
        # set the road map from the scenario file
        if self.scenario:
            self.parse_road_map()

    
    def parse_road_map(self):
        self.road_map = {}
        
        if self.scenario.road_map:
            # convert the road_map string to a map
            for road_string in self.scenario.road_map:
                road_split = road_string.split('-')
                if len(road_split) != 2:
                    logging.warning(f'Invalid road map string {road_string}')
                    continue
                
                out_string, in_string = road_split[0], road_split[1]

                out_split = out_string.split('.')
                in_split = in_string.split('.')

                if len(out_split) != 2 or len(in_split) != 2:
                    logging.warning(f'Invalid road map string{road_string}')
                    continue
                
                out_road, out_lane = int(out_split[0]), int(out_split[1])
                in_road, in_lane = int(in_split[0]), int(in_split[1])

                if out_road not in self.road_map:
                    self.road_map[out_road] = {}
                
                if out_lane not in self.road_map[out_road]:
                    self.road_map[out_road][out_lane] = {}
                
                if in_road not in self.road_map[out_road][out_lane]:
                    self.road_map[out_road][out_lane][in_road] = [in_lane]
                else:
                    self.road_map[out_road][out_lane][in_road].append(in_lane)

    
    def add_car(self):
        if self.road_ends:
            road = random.choice(self.road_ends)
            lane = random.choice(road.lanes)

            car_args = CarGenerator.generate_car()

            # check if we can add a car to this lane without causing an accident
            if lane.last_car:
                if lane.last_car.x - lane.last_car.l/2 > car_args['l']/2*PPM + car_args['s_0']*PPM:
                    # can add
                    car = Car(car_args, car_id=self.car_id, lane=lane)
                    self.cars[self.car_id] = car
                    self.car_id += 1
                else:
                    ...
                    # currently does not try to add to a different lane in the failure case.
                    # could alternatively randomly choose another lane from the remaining lanes,
                    # but this could break other traffic rules.
            else:
                car = Car(car_args, car_id=self.car_id, lane=lane)
                self.cars[self.car_id] = car
                self.car_id += 1
        else:
            logging.warning('No road for car to be added to.')


    def change_lanes(self):
        car_id = random.choice(list(self.cars.keys()))
        self.cars[car_id].change_lane()

    
    def add_road(self, road_coords, n_lanes):
        """
        Creates and adds a new Road.
        Returns the added Road
        """
        road = Road(road_coords, n_lanes=n_lanes)
        self.roads.append(road)
        self.road_ends.append(road)
        return road

    
    def add_junction(self, out_road, out_lane, in_road, in_lane):
        """
        Creates a new Road and links it to the previous Road using a Junction.
        Returns the new Road.
        """
        out_road, in_road = self.roads[out_road], self.roads[in_road]
        out_lane, in_lane = out_road.lanes[out_lane], in_road.lanes[in_lane]

        if out_lane.next_junction:
            # there is already a junction existing for this lane - add to it
            junction = out_lane.next_junction
            junction.lane_map[out_lane].append(in_lane)
        else:
            junction = Junction({out_lane: [in_lane]})
            out_lane.next_junction = junction
        
        if junction not in in_lane.prev_junctions:
            in_lane.prev_junctions.append(junction)

        self.junctions.append(junction)
        
    
    def add_roads(self):
        # build the roads
        for road_id, road in enumerate(self.scenario.roads):
            # create the new road
            new_road = Road(road['endpoints'], n_lanes=road['n_lanes'])
            self.roads.append(new_road)
            if road['is_source']:
                self.road_ends.append(new_road)
        
        # build the junctions and connect the roads
        if self.road_map:
            for out_road, out_lanes in self.road_map.items():
                for out_lane, in_roads in out_lanes.items():
                    for in_road, in_lanes in in_roads.items():
                        for in_lane in in_lanes:
                            self.add_junction(out_road, out_lane, in_road, in_lane)
    

    def add_roads_from_path(self, path, n_lanes):
        # path = tuple(((p0, p1) for p0, p1 in zip(path[:-1], path[1:])))

        # for road_id, endpoints in enumerate(path):
        #     # create the new road
        #     new_road = Road(endpoints, n_lanes=n_lanes)
        #     self.roads.append(new_road)

        #     if road_id == 0:
        #         self.road_ends.append(new_road)
        new_road = Road(path, n_lanes=n_lanes)
        self.roads.append(new_road)
        self.road_ends.append(new_road)

    
    def remove_car(self, car_id):
        car = self.cars[car_id]
        if car.trail_car:
            car.trail_car.lead_car = None
        else:
            car.lane.last_car = None
        del car.lane.cars[car_id]
        del self.cars[car_id]


    def clean_roads(self):
        while self.dead_cars:
            car_id = self.dead_cars.pop()
            self.remove_car(car_id)


    def update(self):
        for car_id, car in self.cars.items():
            if car_id not in self.dead_cars:
                if not car.update():
                    # car has reached the end of its path
                    # check if there is a junction
                    if car.lane.next_junction:
                        # change to that road potentially
                        car.cross_junction()
                        ...
                    else:
                        self.dead_cars.append(car_id)
                        car.x = car.lane.length
        
        self.clean_roads()
        
        if self.roads:
            self.ticks_since_car += 1
            if self.ticks_since_car >= 150/len(self.road_ends):
                self.add_car()
                self.ticks_since_car = 0
            
            self.ticks_since_lane_change += 1
            if self.ticks_since_lane_change >= 400:
                self.change_lanes()
                self.ticks_since_lane_change = 0


    def run_sim(self):
        for tick in range(self.sim_len):
            self.movement()