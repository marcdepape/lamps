# SUB + PUB setup
import zmq
import json
from time import sleep

class LampProxy(object):
    def __init__(self):
        #SUB PUB
        context = zmq.Context()

        # SUB
        self.frontend = context.socket(zmq.SUB)
        self.frontend.bind("tcp://*:8101")

        # PUB
        self.backend = context.socket(zmq.PUB)
        self.backend.bind("tcp://*:8100")
        self.backend.set_hwm(1)

        # SUBSCRIBE TO ALL
        self.frontend.setsockopt(zmq.SUBSCRIBE, b'')
        self.frontend.set_hwm(1)

        # control variables
        self.running = False

        # MESSAGE KEYS
        self.rate = 0.025
        self.peak = 0.25
        self.position = [-1,-1,-1,-1]
        self.lamp_ip = [-1,-1,-1,-1]
        self.listeners = [-1,-1,-1,-1]
        self.broadcast = [-1,-1,-1,-1]
        self.log = "waiting..."
        self.receive = ""
        self.live = 0
        self.message = json.dumps({"ip": -1, "lamp": -1, "rate": self.rate, "peak": self.peak, "live": -1, "position": -1, "listen": -1, "broadcast": -1, "console": self.log}, sort_keys=True)

    def stop(self):
        self.running = False

    def start(self):
        self.setup()
        while self.running == True:
            self.receive = self.frontend.recv_json()
            self.receive = json.loads(self.receive)
            lamp = self.receive["lamp"]
            log = ""
            if "console" in self.receive:
                log = self.receive["console"]
            self.message = json.dumps({"ip": self.lamp_ip, "lamp": lamp, "rate": self.rate, "peak": self.peak, "live": self.live, "position": self.position[lamp], "listen": self.listeners[lamp], "broadcast": -1, "console": log}, sort_keys=True)
            self.backend.send_json(self.message)

    def setup(self):
        while self.live != 1:
            self.receive = self.frontend.recv_json()
            self.receive = json.loads(self.receive)
            print self.receive
            self.lamp_ip[self.receive["lamp"]] = self.receive["ip"]

            num = 0
            for l in range(0,len(self.lamp_ip)):
                if self.lamp_ip[l] == -1:
                    num = num
                else:
                    num = num + 1

            if num == len(self.lamp_ip):
                self.live = 1
                self.running = True
