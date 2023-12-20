import dearpygui.dearpygui as dpg

from car import Car
from road import Road
from parameters import *

import logging
import random

class Simulation:
    def __init__(self, sim_len=50):
        self.cars = {}
        self.roads = []
        self.stopped = []
        self.fps = 60
        self.ticks_since_car = 0
        self.car_id = 0

    
    def add_car(self):
        if self.roads:
            road = random.choice(self.roads)
            lane = random.choice(road.lanes)

            car = Car(car_id=self.car_id, lane=lane)
            self.cars[self.car_id] = car
            lane.cars[self.car_id] = car
            self.car_id += 1
        
        else:
            logging.warning('No road for car to be added to.')


    
    def add_road(self):
        self.roads.append(Road(((0, 150), (1000, 150))))
        self.roads.append(Road(((50, 200), (750, 400))))
        self.roads.append(Road(((1000, 200), (0, 200))))

    
    def remove_car(self, car_id):
        car = self.cars[car_id]
        del car.lane.cars[car_id]
        del self.cars[car_id]


    def clean_roads(self):
        while self.stopped:
            car_id = self.stopped.pop()
            self.remove_car(car_id)


    def update(self):
        for car_id, car in self.cars.items():
            if car_id not in self.stopped:
                if not car.update():
                    # car has reached the end of its path
                    self.stopped.append(car_id)
                    car.x = 1.0
        
        self.clean_roads()
        
        self.ticks_since_car += 1
        if self.ticks_since_car >= 200:
            self.add_car()
            self.ticks_since_car = 0


    def run_sim(self):
        for tick in range(self.sim_len):
            self.movement()


class Window:
    def __init__(self):
        # initialize
        self.setup_dpg()
        self.setup_canvas()
        self.setup_sim()
    

    def handle_add_car(self):
        if self.sim:
            self.sim.add_car()


    # initialization calls to dpg
    def setup_dpg(self):
        dpg.create_context()
        dpg.create_viewport(title='Traffic Sim')
        dpg.setup_dearpygui()
    

    def setup_canvas(self):
        # "In the case of DPG we call the operating system window the viewport and the DPG windows as windows." - DPG Docs        
        with dpg.window(label='Main Window', tag='Canvas', no_resize=True, no_close=True, pos=(50, 50)) as window:
            ...

        dpg.set_primary_window('Canvas', True)
        # self.CANVAS_WIDTH, self.CANVAS_HEIGHT = dpg.get_item_rect_size(window)
        # print(self.CANVAS_HEIGHT)

        with dpg.window(label='Controls', tag='Controls', no_resize=True, no_close=True, pos=(CANVAS_WIDTH+100, 50)):
            dpg.add_button(label='Add Car', callback=self.handle_add_car)


        
        # dpg.apply_transform('road 1', dpg.create_translation_matrix([250, 250]))

    
    def setup_sim(self):
        self.sim = Simulation()
        self.sim.add_road()
        self.sim.add_car()


    def render_loop(self):
        dpg.delete_item('Canvas', children_only=True)
        # render roads
        for road_id, road in enumerate(self.sim.roads):
            for lane_id, lane in enumerate(road.lanes):
                # dpg.delete_item(f'Road {road_id}.{lane_id}')
                (x1, y1), (x2, y2) = lane.endpoints
                with dpg.draw_node(tag=f'Road {road_id}.{lane_id}', parent='Canvas'):
                    dpg.draw_line((x1, y1), (x2, y2), color=(230, 230, 230, 100), thickness=LANE_WIDTH)


        # render cars
        for car_id, car in self.sim.cars.items():
            # dpg.delete_item(f'Car {car_id}')
            with dpg.draw_node(tag=f'Car {car_id}', parent='Canvas'):
                x1, y1 = car.compute_pos()
                u1, u2 = car.unit_vec
                x2, y2 = x1 + car.l*u1, y1 + car.l*u2
                dpg.draw_line((x1, y1), (x2, y2), color=(50, 50, 250, 200), thickness=LANE_WIDTH-2)
        
        self.update()


    def update(self):
        self.sim.update()


    def show(self):
        dpg.show_viewport()

        # dpg.start_dearpygui() # handles render loop
        # below replaces, start_dearpygui()
        while dpg.is_dearpygui_running():
            # insert here any code you would like to run in the render loop
            # you can manually stop by using stop_dearpygui()
            
            self.CANVAS_WIDTH, self.CANVAS_HEIGHT = dpg.get_item_rect_size('Canvas')
            self.render_loop()
            # print('hi')
            dpg.render_dearpygui_frame()

        dpg.destroy_context()


def main():
    window = Window()
    window.show()
    


if __name__ == '__main__':
    main()