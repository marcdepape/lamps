import serial
from time import sleep
import random
ser = serial.Serial('/dev/ttyAMA0', 57600)

while True:
	send = 't' + str(random.randint(0,180))
	print(send)
	for letter in send:
		ser.write(bytes(letter.encode('ascii')))
		#sleep(0.01)

	lamp_status = ser.readline()
	lamp_values = lamp_status.split(":",2)	
	print("Data point: %s | Reading: %s" % (lamp_values[0], lamp_values[1]))
	sleep(0.1)