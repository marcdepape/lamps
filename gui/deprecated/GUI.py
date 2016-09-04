# SUB + PUB setup
import zmq
import json
import thread
context = zmq.Context()

frontend = context.socket(zmq.SUB)
frontend.bind("tcp://*:8101")

backend = context.socket(zmq.PUB)
backend.bind("tcp://*:8100")
backend.set_hwm(1)

frontend.setsockopt(zmq.SUBSCRIBE, b'')
frontend.set_hwm(1)

# KIVY setup
import kivy
kivy.require('1.9.1')
from kivy.app import App
from kivy.lang import Builder

# KV UI
ui_def = '''
GridLayout:
	cols: 3
	Button:
		text: 'Position: {}'.format(app.position)
		on_press: print("A")

	Button
		text: 'B'
		on_press: print("B")

	Button
		text: 'C'
		on_press: print("C")

	Button
		text: 'D'
		on_press: print("D")

	Button
		text: 'E'
		on_press: print("E")

	Button
		text: 'F'
		on_press: print("F")
'''

# Variables
position = 0
broadcast = 0
count = 0
lamp_gui = 0
position_gui = 0
broadcast_gui = 0

def json_messages():
	message = frontend.recv_json()
	message = json.loads(message)
	global position
	global lamp_gui
	global position_gui
	global broadcast_gui
	
	if message["lamp"] == 1:
		position = message["position"]
		broadcast = 1
		lamp_gui = message["lamp"]
		position_gui = message["position"]
		broadcast_gui = 1
	else:
		broadcast = 0

	message = json.dumps({"lamp": message["lamp"], "position": position, "broadcast": broadcast}, sort_keys=True)
	backend.send_json(message)
	return message

def run_sub_pub(threadName):
	while True:
		update = json_messages()
		global count
		count = count + 1
		print(str(count) + " " + update)

class lamp_network_GUI(App):
	global position
	global lamp_gui
	global position_gui
	global broadcast_gui
	def build(self):
		return Builder.load_string(ui_def)

# GUI + Proxy
thread.start_new_thread(run_sub_pub, ("Sub_Pub", ))
lamp_network_GUI().run()


