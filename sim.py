import dearpygui.dearpygui as dpg

from car import Car, CarGenerator
from road import Road
from parameters import *

import logging
import random

class Simulation:
    def __init__(self, sim_len=50):
        self.cars = {}
        self.roads = []
        self.dead_cars = []
        self.fps = 60
        self.ticks_since_car = 0
        self.ticks_since_lane_change = 0
        self.car_id = 0
        self.changed_car = None


    def generate_car(self):
        ...

    
    def add_car(self):
        if self.roads:
            road = random.choice(self.roads)
            lane = random.choice(road.lanes)

            car_args = CarGenerator.generate_car()
            car = Car(car_args, car_id=self.car_id, lane=lane)
            self.cars[self.car_id] = car
            # print(f'Added car {self.car_id} to the road.')
            # print(f'v_0: {car.v_0}, T: {car.T}, b: {car.b}, a: {car.a}, max_v: {car.max_v}')
            self.car_id += 1
        
        else:
            logging.warning('No road for car to be added to.')


    def change_lanes(self):
        car_id = random.choice(list(self.cars.keys()))
        print(car_id, self.cars[car_id].change_lane())
        self.changed_car = self.cars[car_id]
        print(self.cars)

    
    
    def add_road(self):
        self.roads.append(Road(((0, 250), (1000, 250))))
        self.roads.append(Road(((1000, 300), (0, 300))))
        # self.roads.append(Road(((50, 200), (750, 400))))

    
    def remove_car(self, car_id):
        car = self.cars[car_id]
        print(f'Removing car {car.car_id} with trailing car {car.trail_car}')
        if car.trail_car:
            car.trail_car.lead_car = None
            print(f'Car {car.trail_car} set the lead_car to {car.trail_car.lead_car}')
        else:
            car.lane.last_car = None # ISSUE HERE
        del car.lane.cars[car_id]
        del self.cars[car_id]
        # print(f'Removed car {car.car_id} from the road.')


    def clean_roads(self):
        while self.dead_cars:
            car_id = self.dead_cars.pop()
            self.remove_car(car_id)


    def update(self):
        for car_id, car in self.cars.items():
            if car_id not in self.dead_cars:
                if not car.update():
                    # car has reached the end of its path
                    self.dead_cars.append(car_id)
                    car.x = car.lane.length
        
        self.clean_roads()
        
        self.ticks_since_car += 1
        if self.ticks_since_car >= 100:
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
    def __init__(self):
        # initialize
        self.setup_dpg()
        self.setup_canvas()
        self.setup_sim()
    

    def handle_add_car(self):
        if self.sim:
            self.sim.add_car()

    
    def handle_step(self):
        self.render_loop()
    

    def handle_step_100(self):
        for _ in range(100):
            self.handle_step()
    

    def handle_change_lanes(self):
        if self.sim:
            self.sim.change_lanes()
    
    def handle_log_car(self):
        if self.sim:
            self.sim.changed_car = self.sim.cars[int(dpg.get_value('Log Car ID'))]


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
            dpg.add_button(label='Step', callback=self.handle_step)
            dpg.add_button(label='Step (x100)', callback=self.handle_step_100)
            dpg.add_button(label='Change Lanes', callback=self.handle_change_lanes)

            dpg.add_input_text(label='Log Car ID', tag='Log Car ID')
            dpg.add_button(label='Log Car', callback=self.handle_log_car)

        with dpg.window(label='Logging', tag='Logging', no_close=True, pos=(0, 400), width=1200, height=500):
            ...

        # dpg.apply_transform('road 1', dpg.create_translation_matrix([250, 250]))

    
    def setup_sim(self):
        self.sim = Simulation()
        self.sim.add_road()
        self.sim.add_car()


    def render_loop(self):
        dpg.delete_item('Canvas', children_only=True)
        dpg.delete_item('Logging', children_only=True)

        if self.sim.changed_car:
            diag = self.sim.changed_car.get_diagnostics()
            dpg.add_text(self.sim.changed_car.car_id, parent='Logging')
            for k, v in diag.items():
                dpg.add_text(f'{k}: {v}', parent='Logging')

        # render roads
        for road_id, road in enumerate(self.sim.roads):
            for lane_id, lane in enumerate(road.lanes):
                dpg.add_text(f'{lane_id} with last_car {lane.last_car}: {lane.cars}', parent='Logging')
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
                # dpg.draw_line((x1-90, y1), (x2+90, y2), color=(250, 10, 10, 200), thickness=2)
                # dpg.draw_text((x1, y1), f'{car.v:.2f}', size=10)
                dpg.draw_text((x1, y1), f'{car_id}', size=10)
        
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