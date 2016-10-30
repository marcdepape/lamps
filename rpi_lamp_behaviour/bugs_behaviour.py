# Bugs control program (Client, Server, Microcontroller)
import zmq
from gi.repository import Gst, GObject
import gi
from threading import Thread
from time import sleep
import json
import serial
import subprocess
from ping_all_lamps import PingLamps
from check_status import CheckStatus
from stream_control import LampStream
from multiprocessing import Process, Queue


# RPI HOSTNAME
this_lamp = subprocess.check_output('hostname')
this_lamp = int(this_lamp.replace("lamp","",1))

# RPI IP ADDRESS
net = subprocess.Popen(('ifconfig', 'wlan0'), stdout=subprocess.PIPE)
ip = subprocess.check_output(('grep', 'addr'), stdin=net.stdout)
net.wait()
lamp_ip = ip.strip().split("addr:")
lamp_ip = lamp_ip[1].split(" ")
lamp_ip = lamp_ip[0]

# SERVER
server_context = zmq.Context()
server = server_context.socket(zmq.PUB)
server.connect("tcp://armadillo.local:8101")
#server.connect("tcp://bison.local:8101")
server.set_hwm(1)

# CLIENT
client_context = zmq.Context()
client = client_context.socket(zmq.SUB)
client.connect("tcp://armadillo.local:8100")
#client.connect("tcp://bison.local:8100")
client.setsockopt(zmq.SUBSCRIBE, b'')
client.set_hwm(1)

# PING OTHER LAMPS
ping_all = PingLamps(this_lamp)

# CHECK ATMEGA
check_lamp = CheckStatus()

# INITIALIZE STREAMING
GObject.threads_init()
Gst.init(None)

mainloop = GObject.MainLoop()
m = Thread(name="mainloop", target=mainloop.run)
m.daemon = True
m.start()

# LAMP STREAMS
this_stream = LampStream(0.05)

# LAMP VARIABLES
motor_position = 0
broadcast = 0
listening = -1
live_audio = -1
to_lamp = -1
lamp_addresses = [-1,-1,-1,-1]
count = -1
out_update = json.dumps({"ip": lamp_ip,"lamp": this_lamp, "position": motor_position}, sort_keys=True)

def lamp_server():
    while True:
        out_update = json.dumps({"ip": lamp_ip,"lamp": this_lamp, "position": motor_position}, sort_keys=True)
        server.send_json(out_update)
        sleep(0.1)

def update_lamp(update):
    update = json.loads(update)
    if update["lamp"] == this_lamp:
        #print("NEW: " + str(update))
        global broadcast
        broadcast = update["broadcast"]

        global motor_position
        motor_position = update["position"]

        global lamp_addresses
        lamp_addresses = update["ip"]

        global count
        count = update["count"]

        global to_lamp
        to_lamp = update["listen"]
    else:
        pass

def audio_testX():
    vol = Queue()
    play = Queue()
    t1 = Process(name='listen1', target=this_stream.listen, args=(vol, play, "rtsp://192.168.100.162:8554/mic",))
    print "START!"
    t1.start()
    print "SUCCESS?"
    while this_stream.state(play) == False:
        pass
    this_stream.fade(vol, "in")
    sleep(5)
    this_stream.fade(vol, "out")
    sleep(1)
    print "STOP!"
    t1.terminate()

def audio_test():
    lamp_stream = start_stream()
    sleep(10)
    stop_stream(lamp_stream)

def start_stream():
    vol = Queue()
    play = Queue()
    lamp_stream = Process(name='listen', target=this_stream.listen, args=(vol, play, "rtsp://192.168.100.162:8554/mic",))
    print "START!"
    lamp_stream.start()
    while this_stream.state(play) == False:
        pass
    this_stream.fade(vol, "in")
    return lamp_stream

def stop_stream(lamp_stream):
    print "STOP!"
    vol = Queue()
    this_stream.fade(vol,"out")
    lamp_stream.terminate()

class AudioControl(object):

    def __init__(self, this_stream):
        self.this_stream = this_stream
        self.lamp_stream = ""
        self.vol = Queue()
        self.play = Queue()

    def test(self):
        self.start_stream()
        sleep(3)
        self.stop_stream()

    def start_stream(self):
        self.lamp_stream = Process(name='listen', target=self.this_stream.listen, args=(self.vol, self.play, "rtsp://192.168.100.162:8554/mic",))
        print "START!"
        self.lamp_stream.start()
        while self.this_stream.state(self.play) == False:
            pass
        self.this_stream.fade(self.vol, "in")

    def stop_stream(self):
        print "STOP!"
        self.this_stream.fade(self.vol,"out")
        self.lamp_stream.terminate()

audio = AudioControl(this_stream)

#---------------------------------------------------------------------------------------------
# THREADS
p = Thread(name='ping_all_other_lamps', target=ping_all.forever)
l = Thread(name='check_lamp_atmega', target=check_lamp.forever)
s = Thread(name='lamp_server', target=lamp_server)
a = Thread(name='audio_test', target=audio.test)

# SET THREADS
p.daemon = True
l.daemon = True
s.daemon = True
a.daemon = True

if __name__ == '__main__':
    p.start()
    l.start()
    s.start()
    a.start()
    while True:
        update_lamp(client.recv_json())
        motor_position = check_lamp.update(broadcast, motor_position)
        ping_all.update(lamp_addresses)
