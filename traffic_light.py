import time
from threading import Event, Thread
import queue

class TrafficLight:
    def __init__(self, name, state):
        self.name = str(name)
        self.current_state = state

    def progress(self):
        if self.current_state == "green":
            print(self.name + " light yellow")
            self.current_state = "yellow"
        elif self.current_state == "yellow":
            print(self.name + " light red")
            self.current_state = "red"
        elif self.current_state == "red":
            print(self.name + " light green")
            self.current_state = "green"


class TrafficSystem:
    states = {
        "red": 30,
        "yellow": 5,
        "green": 25
    }

    current_time = 0

    def __init__(self, speed=3):
        self.traffic_lights = {}
        first_light = TrafficLight(1, "red")
        second_light = TrafficLight(2, "green")
        self.traffic_lights['1'] = first_light
        self.traffic_lights['2'] = second_light

        self.speed = speed
        self.button_pressed = Event()
        self.button_eligible = False

        self.event_queue = queue.Queue()
        Thread(target=self.timer_thread, args=(self.traffic_lights['1'],), daemon=True).start()
        Thread(target=self.timer_thread, args=(self.traffic_lights['2'],), daemon=True).start()

        self.start_traffic()

    def start_traffic(self):
        while True:
            event = self.event_queue.get().split(" ")

            if event[0] == "progress":
                self.traffic_lights[event[1]].progress()

    def timer_thread(self, light):
        self.event_queue.put('progress ' + light.name)
        time.sleep(self.states[light.current_state] / (self.speed * 2))
        self.button_eligible = True
        time.sleep(self.states[light.current_state] / (self.speed * 2))
        self.button_eligible = False
        self.timer_thread(light)

