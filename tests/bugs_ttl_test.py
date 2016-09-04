import serial
from time import sleep
import random
ser = serial.Serial('/dev/ttyAMA0', 57600)

send = "321,654,987,-"

while True:
	send = ""
	for reading in xrange(1,4):
		send = send + str(random.randint(0,9999)) + ","
	send = send + "-"
	print(send)
	for letter in send:
		ser.write(bytes(letter.encode('ascii')))
		sleep(0.01)

	lamp_status = ser.readline()
	lamp_values = lamp_status.split(" ")	
	print(lamp_values)
	sleep(1)
	