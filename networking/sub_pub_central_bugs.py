# lamp pub-sub-proxy

import zmq
import json
context = zmq.Context()

# This is where the weather server sits
frontend = context.socket(zmq.SUB)
frontend.bind("tcp://*:8101")

# This is our public endpoint for subscribers
backend = context.socket(zmq.PUB)
backend.bind("tcp://*:8100")
backend.set_hwm(1)

# Subscribe on everything
frontend.setsockopt(zmq.SUBSCRIBE, b'')
frontend.set_hwm(1)

position = 0
broadcast = 0
count = 0

def json_messages():
	# Process all parts of the message
    message = frontend.recv_json()
    message = json.loads(message)
    global position

    if message["lamp"] == 1:
    	position = message["position"]
    	broadcast = 1
    else:
    	broadcast = 0

    message = json.dumps({"lamp": message["lamp"], "position": position, "broadcast": broadcast}, sort_keys=True)
    backend.send_json(message)
    return message

# Shunt messages out to our own subscribers
while True:
    update = json_messages()
    count = count + 1
    print(str(count) + " " + update)
