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

    def __init__(self, speed=5):
        self.traffic_lights = [TrafficLight(1, "red"), TrafficLight(2, "green")]
        self.speed = speed
        self.button_pressed = Event()
        self.button_eligible = False

        self.event_queue = queue.Queue()
        Thread(target=self.timer_thread, args=(self.traffic_lights[0],), daemon=True).start()
        Thread(target=self.timer_thread, args=(self.traffic_lights[1],), daemon=True).start()
        Thread(target=self.button_thread, daemon=True).start()

        self.events = {
            'progress': lambda x: self.advance_all_lights(),
            'button_pressed': lambda x: self.advance_all_lights() if self.button_eligible,
        }

        self.start_traffic()

    def start_traffic(self):
        while True:
            evt = self.event_queue.get()
            self.events(evt).call()

    def advance_all_lights(self):
        [light.progress() for light in self.traffic_lights]

    def timer_thread(self, light):
        self.event_queue.put('progress')
        time.sleep(self.states[light.current_state] / (self.speed * 2))
        self.button_eligible = True
        time.sleep(self.states[light.current_state] / (self.speed * 2))
        self.button_eligible = False
        self.timer_thread(light)

    def button_thread(self):
        self.event_queue.put('button_pressed')

    def register(self, event_name, event):
        """
        Allows you to register your own events for the traffic light to respond to

        :param event_name: A string—The name of the event you'd like to register the traffic light to respond to
        :param event: A lambda—how you would like the traffic light to respond
        :return: Nothing if successful: A string if the event name is already taken
        """
        name = str(event_name)

        if name in self.events.keys():
            return "Sorry, that event name is already taken."

        self.events[name] = event

    def notify(self, event_name):
        """
        Allows you to call the events you registered on the traffic light

        :param event_name: A string—the name of the event you'd like to notify the traffic light of
        :return: Nothing if successful: A string if the traffic light doesn't know about that event name
        """
        name = str(event_name)

        if name not in self.events.keys():
            return "Sorry, that event name is not registered."

        self.event_queue.put(name)
