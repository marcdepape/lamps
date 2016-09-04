import smbus
from time import sleep

bus = smbus.SMBus(1)
LAMP_ADDRESS = 0x04
rest = 0.01

def read_data(slave, bytes):
	data=[0] * bytes
	try:
		for i in range(0, bytes):
			data[i] = (bus.read_byte(slave))
			sleep(rest)

		val = (data[0]*256) + data[1]
		print(val)
		return val
	except IOError:
		print("Read Error")
		return -1

def write_data(slave, command, data):
	try:
		bus.write_word_data(slave, ord(command), data)
		sleep(rest)
		return 1
	except IOError:
		print("Write Error")
		return -1

def send_command(slave, command, data):
	status = 0
	check = -1
	while status != 1:
		status = write_data(LAMP_ADDRESS, command, data)
		if status == -1:
			return -1
	while int(check) != int(data):
		check = read_data(LAMP_ADDRESS, 2)
		if check == -1:
			return 1
	return 1

while True:
	send_data = input("Color: 0 - 255 ")

	write_data(LAMP_ADDRESS, 'c', int(send_data))

	read_data(LAMP_ADDRESS, 2)