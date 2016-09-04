
import time
import zmq
import json

context = zmq.Context()
server = context.socket(zmq.REP)
server.bind("tcp://*:8100")

position = 0
broadcast = 0
count = 0

def json_messages():
	# Process all parts of the message
    message = server.recv_json()
    message = json.loads(message)
    global position

    if message["lamp"] == 1:
    	position = message["position"]
    	broadcast = 1
    else:
    	broadcast = 0

    message = json.dumps({"lamp": message["lamp"], "position": position, "broadcast": broadcast}, sort_keys=True)
    server.send_json(message)
    return message

while True:
	update = json_messages()
	count = count + 1
	print(str(count) + " " + update)
	#time.sleep(0.01)
