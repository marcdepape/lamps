import json
from time import sleep
from threading import Thread
from bugs_proxy_sub_pub import LampProxy

# KIVY setup
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.properties import StringProperty
from kivy.clock import Clock

class BugsDashboard(Widget):
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

    def __init__(self, **kwargs):
        super(BugsDashboard, self).__init__(**kwargs)
        self.proxy = LampProxy()
        self.start_proxy()
        Clock.schedule_interval(self.update_GUI, 0.01)

    def start_proxy(self):
        p = Thread(name='proxy', target=self.proxy.start)
        p.daemon = True
        p.start()

    def update_GUI(self, rt):
        update = json.loads(self.proxy.message)
        lamp = update["lamp"]
        print update
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

class BugsApp(App):
    def build(self):
        return BugsDashboard()

if __name__ == '__main__':
	BugsApp().run()
