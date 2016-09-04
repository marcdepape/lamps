# Bugs control program (Client, Server, Microcontroller)
import zmq
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

# LAMP VARIABLES
this_lamp = 1
motor_position = 0
out_update = json.dumps({"lamp": this_lamp, "broadcast": 0, "position": motor_position}, sort_keys=True)
print("INITIAL OUT: " + out_update)

out_update = json.dumps({"lamp": this_lamp, "position": motor_position}, sort_keys=True)
sleep(1)

def update_lamp(update):
    update = json.loads(update)
    if update["lamp"] == this_lamp:
        if update["broadcast"] == 1:
            send = 'r'
            print(send)
            for letter in send:
                ser.write(bytes(letter.encode('ascii')))
                #sleep(0.01)
        elif update["broadcast"] == 0:
            send = 't' + str(update["position"])
            print(send)
            for letter in send:
                ser.write(bytes(letter.encode('ascii')))
                #sleep(0.01)

        lamp_status = ser.readline()
        lamp_status = lamp_status.rstrip()
        lamp_values = lamp_status.split(":",2)  
        print("Data point: %s | Reading: %s" % (lamp_values[0], lamp_values[1]))
        if lamp_values[0] == "dial":
            global motor_position
            print("DIAL: " + lamp_values[1])
            motor_position = lamp_values[1]
        sleep(1)

while True:
    out_update = json.dumps({"lamp": this_lamp, "position": motor_position}, sort_keys=True)
    server.send_json(out_update)
    update_lamp(client.recv_json())

