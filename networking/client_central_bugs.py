
import time
import zmq
import json

context = zmq.Context()

lamp = [0,0,0,0,0]

lamp1 = context.socket(zmq.REQ)
lamp1.connect("tcp://lamp1.local:8101")

lamp2 = context.socket(zmq.REQ)
lamp2.connect("tcp://lamp2.local:8102")

lamp3 = context.socket(zmq.REQ)
lamp3.connect("tcp://lamp3.local:8103")

lamp4 = context.socket(zmq.REQ)
lamp4.connect("tcp://lamp4.local:8104")

position = 0
broadcast = 0
count = 0
message = json.dumps({"lamp": 1, "position": position, "broadcast": broadcast}, sort_keys=True)

while True:
    for x in xrange(1,5):
        if x == 1:
            broadcast = 1
            message = json.dumps({"lamp": x, "position": position, "broadcast": broadcast}, sort_keys=True)
            lamp1.send_json(message)
            message = lamp1.recv_json()
            print message
            message = json.loads(message)
            position = message["position"]
        elif x == 2:
            broadcast = 0
            message = json.dumps({"lamp": x, "position": position, "broadcast": broadcast}, sort_keys=True)
            lamp2.send_json(message)
            message = json.loads(message)
            message = lamp2.recv_json()
        elif x == 3:
            broadcast = 0
            message = json.dumps({"lamp": x, "position": position, "broadcast": broadcast}, sort_keys=True)
            lamp3.send_json(message)
            message = lamp3.recv_json()
            message = json.loads(message)
        elif x == 4:
            broadcast = 0
            message = json.dumps({"lamp": x, "position": position, "broadcast": broadcast}, sort_keys=True)
            lamp4.send_json(message)
            message = lamp4.recv_json()
            message = json.loads(message)

        message = json.dumps({"lamp": x, "position": position, "broadcast": broadcast}, sort_keys=True)
        print(str(count) + " " + message)

        count = count + 1
        #time.sleep(0.01)
