# Bugs control program (Client, Server, Microcontroller)
import zmq
import thread
from time import sleep
import json
import random
import socket
import serial
import subprocess
import os
ser = serial.Serial('/dev/ttyAMA0', 57600)

# RPI HOSTNAME
this_lamp = socket.gethostname()
this_lamp = int(this_lamp.replace("lamp","",1))
print this_lamp

# RPI IP ADDRESS
ip = os.popen('ifconfig wlan0 | grep "inet\ addr"')
lamp_ip = ((ip.read()).strip()).split("addr:")
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

# LAMP VARIABLES
motor_position = 0
broadcast = 0
lamp_is_live = 0
lamp_addresses = [-1,-1,-1,-1]
out_update = json.dumps({"ip": lamp_ip,"lamp": this_lamp, "live": lamp_is_live, "position": motor_position}, sort_keys=True)

def lamp_server(threadName):
    while True:
        out_update = json.dumps({"ip": lamp_ip,"lamp": this_lamp, "live": lamp_is_live, "position": motor_position}, sort_keys=True)
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
    else:
        pass

def lamp_status(threadName):
    while True:
        global broadcast
        if broadcast == 1:
            send = 'r'
            for letter in send:
                ser.write(bytes(letter.encode('ascii')))
            lamp_status = ser.readline()
            lamp_status = lamp_status.rstrip()
            lamp_values = lamp_status.split(":",2)
            if lamp_values[0] == "dial":
                global motor_position
                motor_position = lamp_values[1]
        elif broadcast == 0:
            send = 't' + str(motor_position)
            for letter in send:
                ser.write(bytes(letter.encode('ascii')))
                #sleep(0.01)
            lamp_status = ser.readline()
            lamp_status = lamp_status.rstrip()
            lamp_values = lamp_status.split(":",2)
        sleep(0.1)

def ping_all_lamps(addresses):
    #print addresses
    for ping in range(0,len(addresses)):
        if ping != this_lamp:
            if addresses[ping] != -1:
                check = True
                while check:
                    try:
                        res = subprocess.check_output(['sudo','ping','-q','-c','1', addresses[ping]],universal_newlines=True)
                        res = res.split(",")
                        res = res[1].split(" ")
                        status = res[1]
                        status = int(status)
                        #print "ping to Lamp" + str(ping), addresses[ping], "OK"
                        check = False
                    except subprocess.CalledProcessError as e:
                        #print "no response from Lamp" + str(ping), addresses[ping]
                        check = True

def ping_forever(threadName):
    while True:
        ping_all_lamps(lamp_addresses)
        sleep(2)

thread.start_new_thread(lamp_server, ("Server", ))
thread.start_new_thread(lamp_status, ("Lamp", ))
thread.start_new_thread(ping_forever, ("Ping", ))
sleep(1)

while True:
    update_lamp(client.recv_json())
