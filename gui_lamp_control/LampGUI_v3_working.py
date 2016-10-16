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
broadcast = [1,0,0,0]
lamp_ip = [-1,-1,-1,-1]
go_live = 0
to_lamp = 1
message = json.dumps({"count": count, "ip": lamp_ip, "lamp": -1, "live": -1, "position": position, "broadcast": broadcast[0], "ip": -1}, sort_keys=True)

def lamp_sub_pub(threadName):
	sleep(2)
	while True:
		message = frontend.recv_json()
		message = json.loads(message)
		#print message

		global count
		global position
		global broadcast
		global message
		global to_lamp

		global lamp_ip
		lamp_ip[message["lamp"]-1] = message["ip"]

		if go_live != 1:
			all_lamps_live(lamp_ip)

		count = count + 1

		if count > 2000:
			count = 0;
			to_lamp = to_lamp + 1;
			if to_lamp > 3:
				to_lamp = 1

		if broadcast[message["lamp"]-1] == 1:
			position = message["position"]

		message = json.dumps({"count": count, "ip": lamp_ip, "lamp": message["lamp"], "live": go_live, "position": position, "broadcast": broadcast[message["lamp"]-1], "listen": to_lamp}, sort_keys=True)
		backend.send_json(message)
		print(message)

def all_lamps_live(lamp_addresses):
	global go_live
	num = 0
	for l in range(0,len(lamp_addresses)):
		if lamp_addresses[l] == -1:
			#print str(l) + " EMPTY!"
			pass
		else:
			#print str(l) + "LAMP!"
			num = num + 1

	if num == len(lamp_addresses):
		print "ALL LAMPS!"
		go_live = 1

# GUI begins
def lamps_ui_update():
	global message
	return message

def broadcast_toggle(lamp):
	global broadcast

	for x in xrange(0,len(broadcast)):
		if x == lamp-1:
			broadcast[x] = 1
		else:
			broadcast[x] = 0
	return broadcast

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
	broadcast_state1_GUI = StringProperty()
	broadcast_state2_GUI = StringProperty()
	broadcast_state3_GUI = StringProperty()
	broadcast_state4_GUI = StringProperty()
	broadcast_state5_GUI = StringProperty()
	broadcast_state6_GUI = StringProperty()
	broadcast_state1_GUI = 'normal'
	broadcast_state2_GUI = 'normal'
	broadcast_state3_GUI = 'normal'
	broadcast_state4_GUI = 'normal'
	broadcast_state5_GUI = 'normal'
	broadcast_state6_GUI = 'normal'


	def __init__(self, **kwargs):
		super(UpdateWidget, self).__init__(**kwargs)
		broadcast_GUI = "POSITION"
		position_GUI = "BROADCAST"
		Clock.schedule_interval(self.update_GUI, 0.01)

	def update_GUI(self, rt):
		update = lamps_ui_update()
		if type(update) is str:
			update = json.loads(update)
			if update["lamp"] == 1:
				self.position_lamp1_GUI = str(update["position"])
				if update["broadcast"] == 1:
					self.broadcast_lamp1_GUI = "Broadcast"
				else:
					self.broadcast_lamp1_GUI = "Listen"
			if update["lamp"] == 2:
				self.position_lamp2_GUI = str(update["position"])
				if update["broadcast"] == 1:
					self.broadcast_lamp2_GUI = "Broadcast"
				else:
					self.broadcast_lamp2_GUI = "Listen"
			if update["lamp"] == 3:
				self.position_lamp3_GUI = str(update["position"])
				if update["broadcast"] == 1:
					self.broadcast_lamp3_GUI = "Broadcast"
				else:
					self.broadcast_lamp3_GUI = "Listen"
			if update["lamp"] == 4:
				self.position_lamp4_GUI = str(update["position"])
				if update["broadcast"] == 1:
					self.broadcast_lamp4_GUI = "Broadcast"
				else:
					self.broadcast_lamp4_GUI = "Listen"
		else:
			return -1

	def broadcast_or_listen(self, lamp):
		broadcast_toggle(lamp)

class LampApp(App):
	sleep(5)
	def build(self):
		return UpdateWidget()

thread.start_new_thread(lamp_sub_pub, ("Sub_Pub", ))
if __name__ == '__main__':
	LampApp().run()
