import zmq
import json
import thread
context = zmq.Context()

import kivy
kivy.require('1.9.1')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.uix.gridlayout import GridLayout

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

lamp_gui = 0
position_gui = 0
broadcast_gui = 0

def json_messages():
	# Process all parts of the message
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

class MainGUI(App):
	
	def build(self):
		layout = GridLayout(cols=2)
		layout.add_widget(Button(text=str(lamp_gui)))
		layout.add_widget(Button(text=str(position_gui)))
		layout.add_widget(Button(text=str(broadcast_gui)))
		layout.add_widget(Button(text=str(count)))
		return layout

thread.start_new_thread(run_sub_pub, ("Sub_Pub", ))

if __name__ == '__main__':
	MainGUI().run()
	