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

number_of_lamps = 5

class BugsDashboard(GridLayout):
    lamp0_position = StringProperty()
    lamp0_ip = StringProperty()
    lamp0_log_0 = StringProperty()
    lamp0_log_1 = StringProperty()
    lamp0_log_2 = StringProperty()
    lamp0_log_3 = StringProperty()
    lamp0_log_4 = StringProperty()

    lamp1_position = StringProperty()
    lamp1_ip = StringProperty()
    lamp1_log_0 = StringProperty()
    lamp1_log_1 = StringProperty()
    lamp1_log_2 = StringProperty()
    lamp1_log_3 = StringProperty()
    lamp1_log_4 = StringProperty()

    lamp2_position = StringProperty()
    lamp2_ip = StringProperty()
    lamp2_log_0 = StringProperty()
    lamp2_log_1 = StringProperty()
    lamp2_log_2 = StringProperty()
    lamp2_log_3 = StringProperty()
    lamp2_log_4 = StringProperty()

    lamp3_position = StringProperty()
    lamp3_ip = StringProperty()
    lamp3_log_0 = StringProperty()
    lamp3_log_1 = StringProperty()
    lamp3_log_2 = StringProperty()
    lamp3_log_3 = StringProperty()
    lamp3_log_4 = StringProperty()

    lamp4_position = StringProperty()
    lamp4_ip = StringProperty()
    lamp4_log_0 = StringProperty()
    lamp4_log_1 = StringProperty()
    lamp4_log_2 = StringProperty()
    lamp4_log_3 = StringProperty()
    lamp4_log_4 = StringProperty()

    lamp5_position = StringProperty()
    lamp5_ip = StringProperty()
    lamp5_log_0 = StringProperty()
    lamp5_log_1 = StringProperty()
    lamp5_log_2 = StringProperty()
    lamp5_log_3 = StringProperty()
    lamp5_log_4 = StringProperty()

    timer = 0
    start_time = time()
    current_time = StringProperty()
    current_peak = StringProperty()

    def __init__(self, num, **kwargs):
        super(BugsDashboard, self).__init__(**kwargs)

        self.number_of_lamps = num
        self.proxy = LampProxy(self.number_of_lamps)
        self.start_proxy()
        self.set_peak = 0.5

        self.listen_ids = [[0 for i in range(self.number_of_lamps)] for i in range(self.number_of_lamps)]
        self.broadcast_ids = [0 for i in range(self.number_of_lamps)]
        self.status_ids = [[0 for i in range(self.number_of_lamps)] for i in range(5)]
        self.get_ids()
        self.shuffle(0)

        Clock.schedule_interval(self.update_GUI, 0.01)
        Clock.schedule_interval(self.shuffle, 30)

    def start_proxy(self):
        p = Thread(name='proxy', target=self.proxy.start)
        p.daemon = True
        p.start()

    def update_GUI(self, rt):
        update = json.loads(self.proxy.message)
        #print update
        lamp = update["lamp"]
        logs = update["console"]
        self.proxy.peak = self.set_peak
        self.current_peak = str(self.proxy.peak)

        m, s = divmod((int(time()) - int(self.start_time)), 60)
        h, m = divmod(m, 60)
        self.current_time = "%d:%02d:%02d" % (h, m, s)

        if lamp == 0:
            self.lamp0_position = str(update["position"])
            self.lamp0_ip = str(update["ip"][lamp])
            self.lamp0_log_0 = logs[4]
            self.lamp0_log_1 = logs[3]
            self.lamp0_log_2 = logs[2]
            self.lamp0_log_3 = logs[1]
            self.lamp0_log_4 = logs[0]
        elif lamp == 1:
            self.lamp1_position = str(update["position"])
            self.lamp1_ip = str(update["ip"][lamp])
            self.lamp1_log_0 = logs[4]
            self.lamp1_log_1 = logs[3]
            self.lamp1_log_2 = logs[2]
            self.lamp1_log_3 = logs[1]
            self.lamp1_log_4 = logs[0]
        elif lamp == 2:
            self.lamp2_position = str(update["position"])
            self.lamp2_ip = str(update["ip"][lamp])
            self.lamp2_log_0 = logs[4]
            self.lamp2_log_1 = logs[3]
            self.lamp2_log_2 = logs[2]
            self.lamp2_log_3 = logs[1]
            self.lamp2_log_4 = logs[0]
        elif lamp == 3:
            self.lamp3_position = str(update["position"])
            self.lamp3_ip = str(update["ip"][lamp])
            self.lamp3_log_0 = logs[4]
            self.lamp3_log_1 = logs[3]
            self.lamp3_log_2 = logs[2]
            self.lamp3_log_3 = logs[1]
            self.lamp3_log_4 = logs[0]
        elif lamp == 4:
            self.lamp4_position = str(update["position"])
            self.lamp4_ip = str(update["ip"][lamp])
            self.lamp4_log_0 = logs[4]
            self.lamp4_log_1 = logs[3]
            self.lamp4_log_2 = logs[2]
            self.lamp4_log_3 = logs[1]
            self.lamp4_log_4 = logs[0]
        elif lamp == 5:
            self.lamp5_position = str(update["position"])
            self.lamp5_ip = str(update["ip"][lamp])
            self.lamp5_log_0 = logs[4]
            self.lamp5_log_1 = logs[3]
            self.lamp5_log_2 = logs[2]
            self.lamp5_log_3 = logs[1]
            self.lamp5_log_4 = logs[0]

    def reset_lamp(self, lamp):
        if lamp != -1:
            self.proxy.exit[lamp] = 1
        else:
            for i in range(self.number_of_lamps):
                self.proxy.exit[i] = 1

    def all_streaming_one(self, lamp):
        print "ALL!"
        listeners = []
        for i in range(self.number_of_lamps):
            if i != lamp:
                listeners.append(lamp)
            else:
                listeners.append(-1)
        self.update_button_state(listeners)

    def shuffle(self, rt):
        print "SHUFFLE!"
        listeners = ["x" for i in range(self.number_of_lamps)]
        broadcasters = 0
        self.assign_listeners(listeners, broadcasters)

    def set_peak(self, peak):
        print "set_peak"
        self.proxy.peak = str(peak)
        listeners = ["x" for i in range(self.number_of_lamps)]
        broadcasters = 0
        self.assign_listeners(listeners, broadcasters)

    def manual_listen(self, lamp, to_lamp):
        print "MANUAL LISTEN"
        listeners = ["x" for i in range(self.number_of_lamps)]
        listeners[lamp] = to_lamp
        listeners[to_lamp] = -1
        broadcasters = 1
        self.assign_listeners(listeners, broadcasters)

    def manual_broadcast(self, lamp):
        print "MANUAL BORADCAST"
        listeners = ["x" for i in range(self.number_of_lamps)]
        listeners[lamp] = -1
        broadcasters = 1
        self.assign_listeners(listeners, broadcasters)

    def assign_listeners(self, listeners, broadcasters):
        print "ASSIGN LISTENERS"
        print listeners
        broadcast_lamps = []
        while broadcasters < int(self.number_of_lamps/2):
            assignment = random.randint(0, self.number_of_lamps-1)
            if listeners[assignment] == "x":
                listeners[assignment] = -1
                broadcasters += 1
                broadcast_lamps.append(assignment)
        print "BROADCASTERS {}".format(listeners)

        for i in range(self.number_of_lamps):
            if listeners[i] == "x":
                while listeners[i] == "x":
                    if not broadcast_lamps:
                        listeners[i] = assignment
                    else:
                        assignment = random.choice(broadcast_lamps)
                        listeners[i] = assignment
                        broadcast_lamps.remove(assignment)
        print "LISTENERS {}".format(listeners)
        self.update_button_state(listeners)

    def update_button_state(self, listeners):
        print "BUTTONS!"
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
        print "END!"

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

class Bugs4App(App):
    def build(self):
        return BugsDashboard(number_of_lamps)

class Bugs5App(App):
    def build(self):
        return BugsDashboard(number_of_lamps)

class Bugs6App(App):
    def build(self):
        return BugsDashboard(number_of_lamps)

if __name__ == '__main__':
    if number_of_lamps == 4:
        print "RUN 4"
        Bugs4App().run()
    elif number_of_lamps == 5:
        print "RUN 5"
        Bugs5App().run()
    elif number_of_lamps == 6:
        print "RUN 6"
        Bugs6App().run()
