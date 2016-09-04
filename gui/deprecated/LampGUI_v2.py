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
lamp = 0

def lamp_sub_pub(threadName):
	sleep(2)
	while True:
		message = frontend.recv_json()
		message = json.loads(message)

		global count
		global position
		global broadcast
		global lamp
		lamp = message["lamp"]
		count = count + 1
	
		if message["lamp"] == 1:
			position = message["position"]
			broadcast = 1
		else:
			broadcast = 0

		message = json.dumps({"count": count, "lamp": message["lamp"], "position": position, "broadcast": broadcast}, sort_keys=True)
		backend.send_json(message)
		#print(message)

def lamps_ui_update():
	global count
	global position
	global broadcast
	global lamp

	update = [lamp, position, broadcast, count]
	return update

class UpdateWidget(Widget):
	position_lamp1_GUI = StringProperty()
	position_lamp2_GUI = StringProperty()
	position_lamp3_GUI = StringProperty()
	position_lamp4_GUI = StringProperty()
	position_lamp5_GUI = StringProperty()
	position_lamp6_GUI = StringProperty()

	broadcast_lamp1_GUI = StringProperty()
	broadcast_lamp2_GUI = StringProperty()
	broadcast_lamp3_GUI = StringProperty()
	broadcast_lamp4_GUI = StringProperty()
	broadcast_lamp5_GUI = StringProperty()
	broadcast_lamp6_GUI = StringProperty()

	def __init__(self, **kwargs):
		super(UpdateWidget, self).__init__(**kwargs)
		broadcast_GUI = "POSITION"
		position_GUI = "BROADCAST"
		Clock.schedule_interval(self.update_GUI, 0.01)

	def update_GUI(self, rt):
		update = lamps_ui_update()
		if update[0] == 1:
			self.position_lamp1_GUI = str(update[1])
			self.broadcast_lamp1_GUI = str(update[2])
		if update[0] == 2:
			self.position_lamp2_GUI = str(update[1])
			self.broadcast_lamp2_GUI = str(update[2])
		if update[0] == 3:
			self.position_lamp3_GUI = str(update[1])
			self.broadcast_lamp3_GUI = str(update[2])
		if update[0] == 4:
			self.position_lamp4_GUI = str(update[1])
			self.broadcast_lamp4_GUI = str(update[2])

class LampApp(App):
	sleep(5)
	def build(self):
		return UpdateWidget()

thread.start_new_thread(lamp_sub_pub, ("Sub_Pub", ))
if __name__ == '__main__':
	LampApp().run()


