import dearpygui.dearpygui as dpg

from car import Car
from parameters import *

class Simulation:
    def __init__(self, sim_len=50):
        self.cars = []
        self.fps = 60
        self.ticks_since_car = 0

    
    def add_car(self):
        self.cars.append(Car())


    def update(self):
        for car in self.cars:
            car.update()
        
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
    

    # initialization calls to dpg
    def setup_dpg(self):
        dpg.create_context()
        dpg.create_viewport(title='Traffic Sim')
        dpg.setup_dearpygui()
    

    def setup_canvas(self):
        # "In the case of DPG we call the operating system window the viewport and the DPG windows as windows." - DPG Docs        
        with dpg.window(label='Main Window', tag='Canvas', no_resize=True, no_close=True, pos=(50, 50)):
            with dpg.drawlist(width=CANVAS_WIDTH, height=CANVAS_HEIGHT):
                with dpg.draw_node(tag='Road 1'):
                    dpg.draw_line((0, 103), (CANVAS_WIDTH, 103), color=(230, 230, 230, 100), thickness=10)
        
        with dpg.window(label='Controls', tag='Controls', no_resize=True, no_close=True, pos=(CANVAS_WIDTH+100, 50)):
                dpg.add_button(label='Step', callback=self.update)
        
        # dpg.apply_transform('road 1', dpg.create_translation_matrix([250, 250]))

    
    def setup_sim(self):
        self.sim = Simulation()
        self.sim.add_car()


    def render_loop(self):
        for car_id, car in enumerate(self.sim.cars):
            dpg.delete_item(f'Car {car_id}')
            with dpg.draw_node(tag=f'Car {car_id}', parent='Canvas'):
                dpg.draw_rectangle((car.x, 100), (car.x+car.l, 106), color=(50, 50, 50, 200), fill=(100, 50, 200, 220))
        
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
            self.render_loop()
            # print('hi')
            dpg.render_dearpygui_frame()

        dpg.destroy_context()


def main():
    window = Window()
    window.show()
    


if __name__ == '__main__':
    main()