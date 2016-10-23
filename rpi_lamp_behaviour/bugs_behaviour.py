# Bugs control program (Client, Server, Microcontroller)
import zmq
import threading
from time import sleep
import json
import serial
import subprocess
from ping_all_lamps import PingLamps
from check_status import CheckStatus

ser = serial.Serial('/dev/ttyAMA0', 57600)

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

# LAMP VARIABLES
motor_position = 0
broadcast = 0
listening = -1
live_audio = -1
lamp_addresses = [-1,-1,-1,-1]
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

        if update["live"] == 1:
            listen_to_lamp(update["listen"], lamp_addresses)
    else:
        pass

def listen_to_lamp(to_lamp, addresses):
    global listening
    if listening != -1:
        pass
    if listening != to_lamp:
        try:
            print "YES!"
            #response = subprocess.check_output('gst-launch-1.0 rtspsrc location=rtsp://' + addresses[to_lamp-1] + ':8554/mic ! queue ! rtpvorbisdepay ! vorbisdec ! audioconvert ! audio/x-raw,format=S32LE,channels=2 ! alsasink device="sysdefault:CARD=sndrpiwsp"',universal_newlines=True,shell=True)
            #response = os.popen('gst-launch-1.0 rtspsrc location=rtsp://' + addresses[to_lamp-1] + ':8554/mic ! queue ! rtpvorbisdepay ! vorbisdec ! audioconvert ! audio/x-raw,format=S32LE,channels=2 ! alsasink device="sysdefault:CARD=sndrpiwsp"')
            #response = subprocess.Popen('gst-launch-1.0 rtspsrc location=rtsp://' + addresses[to_lamp-1] + ':8554/mic ! queue ! rtpvorbisdepay ! vorbisdec ! audioconvert ! audio/x-raw,format=S32LE,channels=2 ! alsasink device="sysdefault:CARD=sndrpiwsp"',universal_newlines=True,shell=True)
            listening = to_lamp
            #thread.start_new_thread(audio_thread, (to_lamp,addresses, "Audio", ))
        except subprocess.CalledProcessError as e:
            print "NO!"
            pass

def audio_thread(to_lamp, addresses, threadName):
    print("NEW audio")
    subprocess.Popen('gst-launch-1.0 rtspsrc location=rtsp://' + addresses[to_lamp-1] + ':8554/mic ! queue ! rtpvorbisdepay ! vorbisdec ! audioconvert ! audio/x-raw,format=S32LE,channels=2 ! alsasink device="sysdefault:CARD=sndrpiwsp"',universal_newlines=True,shell=True)

# THREADS
p = threading.Thread(name='ping_all_other_lamps', target=ping_all.forever)
l = threading.Thread(name='check_lamp_atmega', target=check_lamp.forever)
s = threading.Thread(name='lamp_server', target=lamp_server)

# SET THREADS
p.daemon = True
l.daemon = True
s.daemon = True

if __name__ == '__main__':
    p.start()
    l.start()
    s.start()
    sleep(1)

    while True:
        update_lamp(client.recv_json())
        motor_position = check_lamp.update(broadcast, motor_position)
        ping_all.update(lamp_addresses)
