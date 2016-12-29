import json
from time import sleep, clock, time, strftime
from threading import Thread
import random
from bugs_proxy_sub_pub import LampProxy

# KIVY setup
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock

class BugsDashboard(GridLayout):
    number_of_lamps = 4

    lamp0_position = StringProperty()
    lamp0_ip = StringProperty()
    lamp0_log_0 = StringProperty()
    lamp0_log_1 = StringProperty()
    lamp0_log_2 = StringProperty()
    lamp0_log_3 = StringProperty()
    lamp0_log_4 = StringProperty()

    lamp1_position = StringProperty()
    lamp1_ip = StringProperty()
    lamp1_console = StringProperty()

    lamp2_position = StringProperty()
    lamp2_ip = StringProperty()
    lamp2_console = StringProperty()

    lamp3_position = StringProperty()
    lamp3_ip = StringProperty()
    lamp3_console = StringProperty()

    timer = 0
    start_time = time()
    current_time = StringProperty()
    current_peak = StringProperty()

    listen_ids = [[0 for i in range(number_of_lamps)] for i in range(number_of_lamps)]
    broadcast_ids = [0 for i in range(number_of_lamps)]
    status_ids = [[0 for i in range(number_of_lamps)] for i in range(5)]

    def __init__(self, **kwargs):
        super(BugsDashboard, self).__init__(**kwargs)
        self.proxy = LampProxy()
        self.get_ids()
        self.shuffle(0)
        self.start_proxy()
        Clock.schedule_interval(self.update_GUI, 0.01)
        Clock.schedule_interval(self.shuffle, 20)

    def start_proxy(self):
        p = Thread(name='proxy', target=self.proxy.start)
        p.daemon = True
        p.start()

    def update_GUI(self, rt):
        update = json.loads(self.proxy.message)
        #print update
        lamp = update["lamp"]

        m, s = divmod((int(time()) - int(self.start_time)), 60)
        h, m = divmod(m, 60)
        self.current_time = "%d:%02d:%02d" % (h, m, s)

        self.current_peak = str(self.proxy.peak)

        if lamp == 0:
            self.lamp0_position = str(update["position"])
            self.lamp0_ip = str(update["ip"][lamp])
            logs = update["console"]
            self.lamp0_log_0 = logs[4]
            self.lamp0_log_1 = logs[3]
            self.lamp0_log_2 = logs[2]
            self.lamp0_log_3 = logs[1]
            self.lamp0_log_4 = logs[0]
        elif lamp == 1:
            self.lamp1_position = str(update["position"])
            self.lamp1_ip = str(update["ip"][lamp])
        elif lamp == 2:
            self.lamp2_position = str(update["position"])
            self.lamp2_ip = str(update["ip"][lamp])
        elif lamp == 3:
            self.lamp3_position = str(update["position"])
            self.lamp3_ip = str(update["ip"][lamp])

    def shuffle(self, rt):
        self.assign_listeners("x","x")

    def assign_listeners(self, lamp, to_lamp):
        listeners = ["x" for i in range(self.number_of_lamps)]
        broadcast_lamps = []
        broadcasters = 0

        if lamp != "x":
            listeners[lamp] = to_lamp
            listeners[to_lamp] = -1
            broadcasters += 1

        while broadcasters < int(self.number_of_lamps/2):
            assignment = random.randint(0, self.number_of_lamps-1)
            if listeners[assignment] == "x":
                listeners[assignment] = -1
                broadcasters += 1
                broadcast_lamps.append(assignment)

        for i in range(self.number_of_lamps):
            if listeners[i] == "x":
                while listeners[i] == "x":
                    if not broadcast_lamps:
                        listeners[i] = assignment
                    else:
                        assignment = random.choice(broadcast_lamps)
                        listeners[i] = assignment
                        broadcast_lamps.remove(assignment)

        for i in range(self.number_of_lamps):
            self.broadcast_ids[i].state = "normal"
            for j in range(self.number_of_lamps):
                self.listen_ids[i][j].state = "normal"

        for i in range(self.number_of_lamps):
            if listeners[i] == -1:
                self.broadcast_ids[i].state = "down"
            else:
                self.listen_ids[i][listeners[i]].state = "down"

        print listeners
        self.proxy.listeners = listeners

    def get_ids(self):
        i = 0
        for key in self.ids.items():
            this_id = str(key[0]).split("_")
            if this_id[0] == "listen":
                self.listen_ids[int(this_id[1])][int(this_id[3])] = key[1]
            if this_id[0] == "broadcast":
                self.broadcast_ids[int(this_id[1])] = key[1]
            if this_id[0] == "status":
                self.status_ids[int(this_id[1])][int(this_id[3])] = key[1]

class BugsApp(App):
    def build(self):
        return BugsDashboard()

if __name__ == '__main__':
	BugsApp().run()
