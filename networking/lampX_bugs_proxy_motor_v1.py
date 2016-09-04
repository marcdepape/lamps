# Bugs control program (Client, Server, Microcontroller)
import zmq
import thread
from time import sleep
import json
import random
import serial
ser = serial.Serial('/dev/ttyAMA0', 57600)

# SERVER
server_context = zmq.Context()
server = server_context.socket(zmq.PUB)
server.connect("tcp://armadillo.local:8101")
#server.connect("tcp://bison.local:8101")

# CLIENT
client_context = zmq.Context()
client = client_context.socket(zmq.SUB)
client.connect("tcp://armadillo.local:8100")
#client.connect("tcp://bison.local:8100")
client.setsockopt(zmq.SUBSCRIBE, b'')
client.set_hwm(1)

# LAMP VARIABLES
this_lamp = 1
motor_position = 0
broadcast = 0
out_update = json.dumps({"lamp": this_lamp, "position": motor_position}, sort_keys=True)

def lamp_server(threadName):
    while True:
        out_update = json.dumps({"lamp": this_lamp, "position": motor_position}, sort_keys=True)
        server.send_json(out_update)
        sleep(0.1)

def update_lamp(update):
    update = json.loads(update)
    if update["lamp"] == this_lamp:
        print("NEW: " + str(update))
        global broadcast
        broadcast = update["broadcast"]
        global motor_position
        motor_position = update["position"]
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
        
thread.start_new_thread(lamp_server, ("Server", ))
thread.start_new_thread(lamp_status, ("Lamp", ))
sleep(1)

while True:
    update_lamp(client.recv_json())

