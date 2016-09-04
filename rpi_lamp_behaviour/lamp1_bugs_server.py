# Bugs control program (Client, Server, Microcontroller)
import zmq
import thread
from time import sleep
import json
import random
import serial
ser = serial.Serial('/dev/ttyAMA0', 57600)

#  Prepare our context and sockets
context = zmq.Context()
server = context.socket(zmq.REP)
server.bind("tcp://*:8101")

# LAMP VARIABLES
this_lamp = 1
motor_position = 0
broadcast = 0
out_update = json.dumps({"lamp": this_lamp, "position": motor_position}, sort_keys=True)

def update_lamp(update):
    update = json.loads(update)
    if update["lamp"] == this_lamp:
        print("NEW: " + str(update))
        global broadcast
        broadcast = update["broadcast"]
        global motor_position
        if broadcast == 0:
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

print "START THREAD"
thread.start_new_thread(lamp_status, ("Lamp", ))
sleep(1)

while True:
    in_update = server.recv_json()
    update_lamp(in_update)





    out_update = json.dumps({"lamp": this_lamp, "position": motor_position}, sort_keys=True)
    server.send_json(out_update)
    #sleep(0.01)






