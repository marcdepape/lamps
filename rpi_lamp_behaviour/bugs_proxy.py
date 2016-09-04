# lamp pub-sub-proxy

import zmq

context = zmq.Context()

# This is where the weather server sits
frontend = context.socket(zmq.SUB)
frontend.bind("tcp://*:8101")

# This is our public endpoint for subscribers
backend = context.socket(zmq.PUB)
backend.bind("tcp://*:8100")

# Subscribe on everything
frontend.setsockopt(zmq.SUBSCRIBE, b'')

def json_messages():
	# Process all parts of the message
    message = frontend.recv_json()
    backend.send_json(message)
    return message

# Shunt messages out to our own subscribers
while True:
    update = json_messages()
    print(update)
