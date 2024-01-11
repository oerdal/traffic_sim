import dearpygui.dearpygui as dpg

from car import Car, CarGenerator
from road import Road
from junction import Junction
from parameters import *

import scenarios.scen1 as scen1
import scenarios.scen2 as scen2
import scenarios.scen3 as scen3
import scenarios.scen4 as scen4

import logging
import random
import argparse
import time

class Simulation:
    def __init__(self, scenario, sim_len=50):
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


class Window:
    def __init__(self, interactive=False):
        # config init
        self.interactive = interactive
        self.show_car_ids = False
        self.show_mouse_pos = False

        # interactive controls
        self.active_action = None
        self.road_origin = None

        # visualization initialization
        self.setup_dpg()
        self.setup_canvas()
        self.setup_sim(interactive)


    def handle_add_car(self):
        if self.sim:
            self.sim.add_car()

    
    def handle_add_road(self):
        self.active_action = 'Road'

    
    def handle_step(self):
        self.render_loop()
    

    def handle_step_100(self):
        for _ in range(100):
            self.handle_step()
    

    def handle_change_lanes(self):
        if self.sim:
            self.sim.change_lanes()


    def handle_toggle_car_ids(self):
        self.show_car_ids = not self.show_car_ids

    
    def handle_toggle_mouse_pos(self):
        self.show_mouse_pos = not self.show_mouse_pos

    
    def handle_log_car(self):
        if self.sim:
            self.sim.focused_car = self.sim.cars[int(dpg.get_value('Log Car ID'))]


    # event handling
    def handle_canvas_click(self, sender, app_data):
        # print(f'sender: {sender}, app_data: {app_data}')
        if app_data == 0:
            # left click
            self.handle_left_click()


    def handle_left_click(self):
        if self.active_action == 'Road':
            # wait until the canvas is focused into if it is not already
            # this is cruicial since the button to add a road is in a different window
            # if no wait, the first left click will show coordinates relative to the control window
            while not dpg.is_item_focused('Canvas'):
                ...
            mouse_pos = dpg.get_mouse_pos(local=False)
            if self.road_origin:
                # terminate road
                print(f'{self.road_origin} - {mouse_pos}')
                self.sim.add_road((self.road_origin, mouse_pos), 10)
                self.road_origin = None
            else:
                self.road_origin = mouse_pos


    # initialization calls to dpg
    def setup_dpg(self):
        dpg.create_context()
        dpg.create_viewport(title='Traffic Sim', width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        dpg.setup_dearpygui()
    

    def setup_canvas(self):

        # "In the case of DPG we call the operating system window the viewport and the DPG windows as windows." - DPG Docs        
        with dpg.window(label='Main Window', tag='Canvas', no_title_bar=True, no_resize=True, no_close=True) as window:
            dpg.add_text("Click me with any mouse button", tag="text item")

        with dpg.handler_registry(tag='Canvas Click Handler'):
            dpg.add_mouse_click_handler(callback=self.handle_canvas_click)

        dpg.set_primary_window('Canvas', True)
        # self.CANVAS_WIDTH, self.CANVAS_HEIGHT = dpg.get_item_rect_size(window)

        with dpg.window(label='Moderation', tag='Moderation', no_resize=True, no_close=True, pos=(CANVAS_WIDTH-250, 50), width=200):
            dpg.add_button(label='Step', callback=self.handle_step)
            dpg.add_button(label='Step (x100)', callback=self.handle_step_100)
            dpg.add_button(label='Change Lanes', callback=self.handle_change_lanes)
            dpg.add_button(label='Toggle Car IDs', callback=self.handle_toggle_car_ids)
            dpg.add_button(label='Toggle Mouse Pos', callback=self.handle_toggle_mouse_pos)

            dpg.add_input_text(label='Log Car ID', tag='Log Car ID')
            dpg.add_button(label='Log Car', callback=self.handle_log_car)
        
        with dpg.window(label='Controls', tag='Controls', no_resize=True, no_close=True, pos=(CANVAS_WIDTH-250, 550), width=200):
            dpg.add_button(label='Add Car', callback=self.handle_add_car)
            dpg.add_button(label='Add Road', callback=self.handle_add_road)

        with dpg.window(label='Logging', tag='Logging', no_close=True, pos=(50, 750), width=CANVAS_WIDTH-100, height=400):
            ...

        # dpg.apply_transform('road 1', dpg.create_translation_matrix([250, 250]))

    
    def setup_sim(self, interactive=False):
        scenario = scen4
        self.sim = Simulation(scenario=scenario)

        if interactive:
            ...
        else:
            self.sim.add_roads()

        self.sim.add_car()


    def render_loop(self):
        dpg.delete_item('Canvas', children_only=True)
        dpg.delete_item('Logging', children_only=True)

        # LOGGING
        # mouse coords
        if self.show_mouse_pos:
            dpg.add_text(f'mouse: {dpg.get_mouse_pos(local=False)}', parent='Logging')


        # focused car
        if self.sim.focused_car:
            diag = self.sim.focused_car.get_diagnostics()
            dpg.add_text(self.sim.focused_car.car_id, parent='Logging')
            for car_id in diag.values():
                dpg.add_text(car_id, parent='Logging')

        # render junctions
        # for junction_id, junction in enumerate(self.sim.junctions):
        #     for lane_id, (prev_lane, next_lane) in enumerate(junction.lane_map.items()):
        #         (_, _), (x2, y2) = prev_lane.endpoints
        #         (x1, y1), (_, _) = next_lane.endpoints
        #         with dpg.draw_node(tag=f'Junction {junction_id}.{lane_id}', parent='Canvas'):
        #             dpg.draw_line((x1, y1), (x2, y2), color=(150, 150, 150, 200), thickness=LANE_WIDTH)

        # render roads
        for road_id, road in enumerate(self.sim.roads):
            for lane_id, lane in enumerate(road.lanes):
                dpg.add_text(f'Lane {road_id}-{lane_id}: {[car_id for car_id in lane.cars.values()]}', parent='Logging')
                # dpg.delete_item(f'Road {road_id}.{lane_id}')
                (x1, y1), (x2, y2) = lane.endpoints
                with dpg.draw_node(tag=f'Road {road_id}.{lane_id}', parent='Canvas'):
                    dpg.add_text(f'({x1}, {y1}), ({x2}, {y2})', parent='Logging')
                    dpg.draw_line((x1, y1), (x2, y2), color=(120, 120, 120, 210), thickness=LANE_WIDTH)
                
                # render cars
                for car_id, car in lane.cars.items():
                    # dpg.delete_item(f'Car {car_id}')
                    with dpg.draw_node(tag=f'Car {car_id}', parent='Canvas'):
                        x1, y1 = car.compute_pos()
                        u1, u2 = car.unit_vec
                        x2, y2 = x1 + car.l*u1, y1 + car.l*u2
                        dpg.draw_line((x1, y1), (x2, y2), color=(50, 50, 250, 200), thickness=LANE_WIDTH-2)
                        # dpg.draw_line((x1-90, y1), (x2+90, y2), color=(250, 10, 10, 200), thickness=2)
                        # dpg.draw_text((x1, y1), f'{car.v:.2f}', size=10)
                        if self.show_car_ids:
                            dpg.draw_text((x1, y1), f'{car_id}', size=10)
        
        self.update()


    def update(self):
        self.sim.update()

    
    def set_params(self):
        dpg.split_frame()
        self.TITLE_BAR_HEIGHT = dpg.get_text_size('')[1] + 2*DEFAULT_PADDING


    def show(self):
        dpg.show_viewport()

        # dpg.start_dearpygui() # handles render loop
        # below replaces, start_dearpygui()
        while dpg.is_dearpygui_running():
            # insert here any code you would like to run in the render loop
            # you can manually stop by using stop_dearpygui()
            
            # self.CANVAS_WIDTH, self.CANVAS_HEIGHT = dpg.get_item_rect_size('Canvas')
            self.render_loop()
            dpg.render_dearpygui_frame()

        dpg.destroy_context()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '-I', '--interactive', action='store_true')
    args = parser.parse_args()

    window = Window(args.interactive)
    window.show()
    


if __name__ == '__main__':
    main()