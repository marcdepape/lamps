# SUB + PUB setup
import zmq
import json
import thread
from time import sleep
context = zmq.Context()

frontend = context.socket(zmq.SUB)
frontend.bind("tcp://*:8101")

backend = context.socket(zmq.PUB)
backend.bind("tcp://*:8100")
backend.set_hwm(1)

frontend.setsockopt(zmq.SUBSCRIBE, b'')
frontend.set_hwm(1)

# KIVY setup
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import StringProperty
from kivy.clock import Clock

count = 0
position = 0
broadcast = 0
message = ""

def lamp_sub_pub(threadName):
	sleep(2)
	while True:
		message = frontend.recv_json()
		message = json.loads(message)

		global count
		global position
		global broadcast
		global message

		count = count + 1
	
		if message["lamp"] == 1:
			position = message["position"]
			broadcast = 1
		else:
			broadcast = 0

		message = json.dumps({"count": count, "lamp": message["lamp"], "position": position, "broadcast": broadcast}, sort_keys=True)
		backend.send_json(message)
		#print(message)

def lamp_ui_update():
	global message
	return message

class UpdateWidget(Widget):
	position_GUI = StringProperty()
	broadcast_GUI = StringProperty()
	position_status = 0
	broadcast_status = 0

	def __init__(self, **kwargs):
		super(UpdateWidget, self).__init__(**kwargs)
		broadcast_GUI = "POSITION"
		position_GUI = "BROADCAST"
		Clock.schedule_interval(self.update_GUI, 0.01)

	def update_GUI(self, rt):
		message = lamp_ui_update()
		print(message)
		self.position_GUI = str(100)
		self.broadcast_GUI = str(100)
		#print(str(self.position_GUI) + " " + str(self.broadcast_GUI))

class LampApp(App):
	def build(self):
		return UpdateWidget()

thread.start_new_thread(lamp_sub_pub, ("Sub_Pub", ))
if __name__ == '__main__':
	LampApp().run()


