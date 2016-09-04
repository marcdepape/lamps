# Bugs control program (Client, Server, Microcontroller)
import zmq
import thread
from time import sleep
import json
import serial
import random

ser = serial.Serial('/dev/ttyAMA0', 57600)

out_update = json.dumps({"lamp": 1, "motor": 1}, sort_keys=True)

# LAMP VARIABLES
lamp = 3
motor_position = 0

def lamp_server(threadName):
    # SERVER
    server_context = zmq.Context()
    server = server_context.socket(zmq.PUB)
    server.connect("tcp://armadillo.local:8101")
    #server.connect("tcp://bison.local:8101")

    while True:
        global lamp
        global motor_position
        out_update = json.dumps({"lamp": lamp, "position": motor_position}, sort_keys=True)
        server.send_json(out_update)
        sleep(0.01)

def lamp_client(threadName):
    # CLIENT
    client_context = zmq.Context()
    client = client_context.socket(zmq.SUB)
    client.connect("tcp://armadillo.local:8100")
    #client.connect("tcp://bison.local:8100")
    client.setsockopt(zmq.SUBSCRIBE, b'')

    while True:
        incoming = client.recv_json()
        print(incoming)
        incoming = json.loads(incoming)
        update_lamp(incoming)

def update_lamp(threadName):
    while True:
        send = 't' + str(random.randint(0,180))
        for letter in send:
            ser.write(bytes(letter.encode('ascii')))
        lamp_status = ser.readline()
        lamp_values = lamp_status.split(":",2)  
        print("Data point: %s | Reading: %s" % (lamp_values[0], lamp_values[1]))
        if lamp_status[0] == "dial":
            global motor_position
            motor_position = lamp_status[1]
        sleep(0.1)

try:
    #thread.start_new_thread(lamp_server, ("Server", ))
    #thread.start_new_thread(lamp_client, ("Client", ))
    thread.start_new_thread(update_lamp, ("Update", ))
except:
    print "Error!"

while True:
    pass    

