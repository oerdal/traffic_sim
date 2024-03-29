import dearpygui.dearpygui as dpg

from car import Car, CarGenerator
from road import Road
from junction import Junction
from sim import Simulation
from parameters import *
from math_functions import get_normal_vector
from bezier import Bezier, LinearBezier

import scenarios.scen1 as scen1
import scenarios.scen2 as scen2
import scenarios.scen3 as scen3
import scenarios.scen4 as scen4

import logging
import random
import argparse
import time

class Window:
    def __init__(self):
        # config init
        self.show_car_ids = False
        self.show_mouse_pos = False

        self.canvas_bounds = [[0, 0], [CANVAS_WIDTH, CANVAS_HEIGHT]]
        self.ppm = 1 # "pixels per meter" - scaling factor

        # visualization initialization
        # rewriting this form to solve inheritence issue
        Window.setup_dpg(self)
        Window.setup_canvas(self)


    def shift_xy(self, x, y):
        return x + self.canvas_bounds[0][0], y + self.canvas_bounds[0][1]


    def unshift_xy(self, x, y):
        return x - self.canvas_bounds[0][0], y - self.canvas_bounds[0][1]
    

    def get_canvas_height(self):
        return self.canvas_bounds[1][1] - self.canvas_bounds[0][1]

    def get_canvas_width(self):
        return self.canvas_bounds[1][0] - self.canvas_bounds[0][0]


    def draw_bezier(self, bezier):
        if isinstance(bezier, LinearBezier):
            P0, P1, P2, P3 = bezier.P0, bezier.P0, bezier.P1, bezier.P1
        else:
            P0, P1, P2, P3 = bezier.P0, bezier.P1, bezier.P2, bezier.P3
        
        # P0, P1, P2, P3 = self.unshift_xy(*P0), self.unshift_xy(*P1), self.unshift_xy(*P2), self.unshift_xy(*P3)
        # dpg.draw_bezier_cubic(P0, P1, P2, P3, color=(100, 100, 100, 200), thickness=LANE_WIDTH)
            
        control_points = [P0, P1, P2, P3]
        for i, (x, y) in enumerate(control_points):
            x *= self.ppm
            y *= self.ppm
            x, y = self.unshift_xy(x, y)
            control_points[i] = [x, y]

        dpg.draw_bezier_cubic(*control_points, color=(100, 100, 100, 200), thickness=LANE_WIDTH)
    

    def draw_crosshair(self, x, y):
        dpg.draw_line((x, y-4), (x, y+5))
        dpg.draw_line((x-4, y), (x+5, y))


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


    def handle_toggle_car_ids(self):
        self.show_car_ids = not self.show_car_ids

    
    def handle_toggle_mouse_pos(self):
        self.show_mouse_pos = not self.show_mouse_pos

    
    def handle_log_car(self):
        if self.sim:
            self.sim.focused_car = self.sim.cars[int(dpg.get_value('Log Car ID'))]


    # initialization calls to dpg
    def setup_dpg(self):
        dpg.create_context()
        dpg.create_viewport(title='Traffic Sim', width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        dpg.setup_dearpygui()
    

    def setup_canvas(self):

        # "In the case of DPG we call the operating system window the viewport and the DPG windows as windows." - DPG Docs        
        with dpg.window(label='Main Window', tag='Canvas', no_title_bar=True, no_resize=True, no_close=True) as window:
            ...

        # adjust canvas theme
        with dpg.theme() as canvas_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0, category=dpg.mvThemeCat_Core)
        
        dpg.bind_item_theme(window, canvas_theme)

        dpg.set_primary_window(window, True)
        # self.CANVAS_WIDTH, self.CANVAS_HEIGHT = dpg.get_item_rect_size(window)

        with dpg.window(label='Moderation', tag='Moderation', no_resize=True, no_close=True, pos=(CANVAS_WIDTH-350, 50), width=300):
            dpg.add_button(label='Step', callback=self.handle_step)
            dpg.add_button(label='Step (x100)', callback=self.handle_step_100)
            dpg.add_button(label='Change Lanes', callback=self.handle_change_lanes)
            dpg.add_button(label='Toggle Car IDs', callback=self.handle_toggle_car_ids)
            dpg.add_button(label='Toggle Mouse Pos', callback=self.handle_toggle_mouse_pos)

            dpg.add_input_text(label='Log Car ID', tag='Log Car ID')
            dpg.add_button(label='Log Car', callback=self.handle_log_car)

        with dpg.window(label='Logging', tag='Logging', no_close=True, pos=(50, 750), width=CANVAS_WIDTH-100, height=400):
            ...

        # dpg.apply_transform('road 1', dpg.create_translation_matrix([250, 250]))

    
    def setup_sim(self):
        scenario = scen4
        self.sim = Simulation(scenario=scenario)

        self.sim.add_roads()


    def render_loop(self):
        dpg.delete_item('Canvas', children_only=True)
        dpg.delete_item('Logging', children_only=True)

        ## LOGGING
        # Mouse position
        if self.show_mouse_pos:
            with dpg.draw_node(tag='Mouse Pos', parent='Canvas'):
                mouse_pos = dpg.get_mouse_pos(local=False)
                dpg.draw_text((mouse_pos[0]-5, mouse_pos[1]-20), f'{mouse_pos}', size=FONT_SIZE)
                self.draw_crosshair(mouse_pos[0], mouse_pos[1])
        
        # Canvas Bounds
        with dpg.draw_node(tag='Canvas Bounds', parent='Canvas'):
            dpg.draw_text((5, 5), f'Canvas Bounds: {self.canvas_bounds}', size=FONT_SIZE)

        # Focused car details
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

        # Render roads
        for road_id, road in enumerate(self.sim.roads):
            for lane_id, lane in enumerate(road.lanes):
                if lane.is_key:
                    continue
                dpg.add_text(f'Lane {road_id}-{lane_id}: {[car_id for car_id in lane.cars.values()]}', parent='Logging')
                # dpg.delete_item(f'Road {road_id}.{lane_id}')
                (x1, y1), (x2, y2) = lane.endpoints
                with dpg.draw_node(tag=f'Road {road_id}.{lane_id}', parent='Canvas'):
                    dpg.add_text(f'({x1}, {y1}), ({x2}, {y2})', parent='Logging')
                    # dpg.draw_polyline(lane.path, color=(120, 120, 120, 210), thickness=LANE_WIDTH)
                    for i, bezier in enumerate(lane.beziers):
                        self.draw_bezier(bezier)

                
                # Render cars
                for car_id, car in lane.cars.items():
                    # dpg.delete_item(f'Car {car_id}')
                    with dpg.draw_node(tag=f'Car {car_id}', parent='Canvas'):
                        x1, y1 = car.compute_pos()
                        # u1, u2 = car.unit_vec
                        u1, u2 = car.compute_orientation()
                        l = car.l*self.ppm/2
                        x1, y1, x2, y2 = x1 - l*u1, y1 - l*u2, x1 + l*u1, y1 + l*u2

                        # canvas navigation
                        x1, y1 = self.unshift_xy(x1, y1)
                        x2, y2 = self.unshift_xy(x2, y2)
                        
                        dpg.draw_line((x1, y1), (x2, y2), color=(50, 50, 250, 200), thickness=LANE_WIDTH*self.ppm-2)

                        # dpg.draw_line((x1-90, y1), (x2+90, y2), color=(250, 10, 10, 200), thickness=2)
                        # dpg.draw_text((x1, y1), f'{car.v:.2f}', size=10)
                        if self.show_car_ids:
                            dpg.draw_text((x1, y1), f'{car_id}', size=FONT_SIZE)
        
        self.update()


    def update(self):
        """
        Perform all simulation related updates.
        Includes, but is not limited to: update car positions and add/change lanes of cars
        """
        self.sim.update()

    
    def set_params(self):
        """
        Currently not used since canvas uses global mouse position.
        """
        self.TITLE_BAR_HEIGHT = dpg.get_text_size('')[1] + 2*DEFAULT_PADDING


    def show(self):
        dpg.show_viewport()

        # dpg.start_dearpygui() # handles render loop
        # below replaces, start_dearpygui()
        while dpg.is_dearpygui_running():
            # "insert here any code you would like to run in the render loop
            # you can manually stop by using stop_dearpygui()"
            
            self.render_loop()
            dpg.render_dearpygui_frame()

        dpg.destroy_context()


class InteractiveWindow(Window):
    def __init__(self):
        super().__init__()

        # interactive controls
        self.active_action = None
        self.road_queue = []

        self.build_wheel = ['Road', 'Junction']
        self.build_wheel_idx = 0

        self.setup_canvas()



    def setup_sim(self):
        self.sim = Simulation()
    

    def handle_add_road(self):
        self.active_action = 'Build'

    
    def handle_clear_canvas(self):
        self.setup_sim()


    # event handling
    def handle_canvas_click(self, sender, app_data):
        # print(f'sender: {sender}, app_data: {app_data}')
        match app_data:
            case 0:
                # left click
                self.handle_left_click()
            case 1:
                # right click
                self.handle_right_click()

    
    def handle_key_press(self, sender, app_data):
        match app_data:
            case 37:
                # left arrow
                self.shift_canvas('L')
            case 38:
                # up arrow
                self.shift_canvas('U')
            case 39:
                # right arrow
                self.shift_canvas('R')
            case 40:
                # down arrow
                self.shift_canvas('D')
            case 65:
                # a
                self.build_wheel_idx = (self.build_wheel_idx - 1) % len(self.build_wheel)
            case 68:
                # d
                self.build_wheel_idx = (self.build_wheel_idx + 1) % len(self.build_wheel)
            case 187:
                # +
                self.zoom_in()
            case 189:
                # -
                self.zoom_out()
        
        dpg.set_value('Current Structure', f'Current Structure: {self.build_wheel[self.build_wheel_idx]}')


    def handle_left_click(self):
        if self.active_action == 'Build':
            # wait until the canvas is focused into if it is not already
            # this is cruicial since the button to add a road is in a different window
            # if no wait, the first left click will show coordinates relative to the control window
            while not dpg.is_item_focused('Canvas'):
                ...
            mouse_pos = self.shift_xy(*dpg.get_mouse_pos(local=False))
            if self.road_queue and mouse_pos == self.road_queue[-1]:
                # terminate road
                self.sim.add_roads_from_path(self.road_queue, int(dpg.get_value('Lane Count')))
                self.road_queue = []
                self.active_action = None
            else:
                # add to the road queue
                self.road_queue.append(mouse_pos)

    
    def handle_right_click(self):
        if self.active_action == 'Build':
            self.road_queue = []
            self.active_action = None

    
    def shift_canvas(self, direction, scale=0.05):
        if direction == 'L' or direction == 'R':
            width = self.canvas_bounds[1][0] - self.canvas_bounds[0][0]
            dx = int(width * scale) if direction == 'R' else int(-width * scale)
            self.canvas_bounds[1][0] += dx
            self.canvas_bounds[0][0] += dx
        
        elif direction == 'U' or direction == 'D':
            height = self.canvas_bounds[1][1] - self.canvas_bounds[0][1]
            dx = int(height * scale) if direction == 'D' else int(-height * scale)
            self.canvas_bounds[1][1] += dx
            self.canvas_bounds[0][1] += dx
        
        dpg.set_value('Canvas Bounds', f'Canvas Bounds: {self.canvas_bounds}')
    

    def zoom_in(self, scale=1.05):
        canvas_width, canvas_height = self.get_canvas_width(), self.get_canvas_height()
        self.ppm *= scale
        self.sim.ppm = self.ppm
        new_width, new_height = canvas_width / scale, canvas_height / scale
        dx, dy = canvas_width - new_width, canvas_height - new_height
        x1, x2 = self.canvas_bounds[0][0] + dx, self.canvas_bounds[1][0] - dx
        y1, y2 = self.canvas_bounds[0][1] + dy, self.canvas_bounds[1][1] - dy
        self.canvas_bounds = [[x1, y1], [x2, y2]]


    
    def zoom_out(self, scale=1.05):
        canvas_width, canvas_height = self.get_canvas_width(), self.get_canvas_height()
        self.ppm /= scale
        self.sim.ppm = self.ppm
        new_width, new_height = canvas_width * scale, canvas_height * scale
        dx, dy = new_width - canvas_width, new_height - canvas_height
        x1, x2 = self.canvas_bounds[0][0] - dx, self.canvas_bounds[1][0] + dx
        y1, y2 = self.canvas_bounds[0][1] - dy, self.canvas_bounds[1][1] + dy
        self.canvas_bounds = [[x1, y1], [x2, y2]]

        
    ## RENDERING
    def render_loop(self):
        super().render_loop()

        if self.road_queue:
            with dpg.draw_node(tag=f'Draw Queue', parent='Canvas'):
                    for x, y in self.road_queue:
                        x, y = self.unshift_xy(x, y)
                        self.draw_crosshair(x, y)


    def setup_canvas(self):
        with dpg.handler_registry(tag='Canvas Click Handler'):
            dpg.add_mouse_click_handler(callback=self.handle_canvas_click)
        
        with dpg.handler_registry(tag='Key Handler'):
            dpg.add_key_press_handler(callback=self.handle_key_press)
        
        with dpg.window(label='Controls', tag='Controls', no_resize=True, no_close=True, pos=(CANVAS_WIDTH-350, 550), width=300):
            dpg.add_button(label='Clear Canvas', callback=self.handle_clear_canvas)
            dpg.add_button(label='Add Car', callback=self.handle_add_car)
            dpg.add_button(label='Add Road', callback=self.handle_add_road)
            dpg.add_text(f'Current Structure: {self.build_wheel[self.build_wheel_idx]}', tag='Current Structure')
            dpg.add_slider_int(label='Lane Count', tag='Lane Count', default_value=3, min_value=1, max_value=10, clamped=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '-I', '--interactive', action='store_true')
    args = parser.parse_args()

    window = InteractiveWindow() if args.interactive else Window()
    window.setup_sim()
    window.show()


if __name__ == '__main__':
    main()