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

    lamp1_broadcast = StringProperty()
    lamp1_listen = StringProperty()
    lamp1_position = StringProperty()
    lamp1_ip = StringProperty()

    lamp2_broadcast = StringProperty()
    lamp2_listen = StringProperty()
    lamp2_position = StringProperty()
    lamp2_ip = StringProperty()

    lamp3_broadcast = StringProperty()
    lamp3_listen = StringProperty()
    lamp3_position = StringProperty()
    lamp3_ip = StringProperty()

    lamp4_broadcast = StringProperty()
    lamp4_listen = StringProperty()
    lamp4_position = StringProperty()
    lamp4_ip = StringProperty()

    timer = 0
    start_time = time()
    current_time = StringProperty()

    listen_ids = [[0 for i in range(number_of_lamps)] for i in range(number_of_lamps)]

    def __init__(self, **kwargs):
        super(BugsDashboard, self).__init__(**kwargs)

        self.proxy = LampProxy()
        self.start_proxy()
        Clock.schedule_interval(self.update_GUI, 0.01)

        self.set_listen()

    def start_proxy(self):
        p = Thread(name='proxy', target=self.proxy.start)
        p.daemon = True
        p.start()

    def update_GUI(self, rt):
        update = json.loads(self.proxy.message)
        lamp = update["lamp"]

        m, s = divmod((int(time()) - int(self.start_time)), 60)
        h, m = divmod(m, 60)
        self.current_time = "%d:%02d:%02d" % (h, m, s)

        if lamp == 1:
            self.lamp1_broadcast = str(update["broadcast"])
            self.lamp1_listen = str(update["listen"])
            self.lamp1_position = str(update["position"])
            self.lamp1_ip = str(update["ip"][lamp-1])
        elif lamp == 2:
            self.lamp2_broadcast = str(update["broadcast"])
            self.lamp2_listen = str(update["listen"])
            self.lamp2_position = str(update["position"])
            self.lamp2_ip = str(update["ip"][lamp-1])
        elif lamp == 3:
            self.lamp3_broadcast = str(update["broadcast"])
            self.lamp3_listen = str(update["listen"])
            self.lamp3_position = str(update["position"])
            self.lamp3_ip = str(update["ip"][lamp-1])
        elif lamp == 4:
            self.lamp4_broadcast = str(update["broadcast"])
            self.lamp4_listen = str(update["listen"])
            self.lamp4_position = str(update["position"])
            self.lamp4_ip = str(update["ip"][lamp-1])
        self.update_lamp_properties(update)

    def update_lamp_properties(self, update):
        if clock() - self.timer > 2.0:
            for l in range(0, self.number_of_lamps):
                self.proxy.to_lamp[l] = 1
            self.timer = clock()

    def change_listen(self, lamp, to_lamp):
        self.assign_listeners()
        self.listen_ids[lamp-1][to_lamp-1].state = "down"
        self.proxy.to_lamp[lamp-1] = to_lamp


    def assign_listeners(self):
        choice = ["x","x","x","x"]
        broadcasters = 0
        while broadcasters < int(self.number_of_lamps/2):
            assignment = random.randint(0, self.number_of_lamps-1)
            if choice[assignment] == "x":
                choice[assignment] = -1
                broadcasters += 1
        print choice

        for i in range(self.number_of_lamps):
            if choice[i] == "x":
                while choice[i] == "x":
                    assignment = random.randint(0, self.number_of_lamps-1)
                    if assignment != i and choice[assignment] == -1:
                        choice[i] = assignment
            else:
                pass

        print choice

    def set_listen(self):
        i = 0
        for key in self.ids.items():
            this_id = str(key[0]).split("_")
            self.listen_ids[int(this_id[1])-1][int(this_id[3])-1] = key[1]

class BugsApp(App):
    def build(self):
        return BugsDashboard()

if __name__ == '__main__':
	BugsApp().run()
