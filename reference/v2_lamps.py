import smbus
import time
import random

cmd = ['c','d','r','t','y','u','d','c','f','c']
bus = smbus.SMBus(1)

LAMP_ADDRESS = 0x04

#reads data from the i2c bus
def readData(slave, bytes): #address, number of bytes to read
        data=[0] * bytes
        try:
                for i in range(0, bytes):
                        data[i] = (bus.read_byte(slave))
                        time.sleep(0.01)
                        print("BYTE" + str(i) + ": " + str(data[i]))
                val = (data[0]*256) + data[1]
                print("READING VALUE: " + str(val))
                return val
        except IOError:
                print("IOError in readData")
                return -1

def writeData(slave, cmd, data):
        try:
                bus.write_word_data(slave,ord(cmd), data)
                time.sleep(0.01) 
                print("SENDING COMMAND: " + str(cmd) + " DATA: " + str(data))
                return 1
        except IOError:
                print("IOError in writeData")
                return -1
                #subprocess.call(['i2cdetect', '-y', '1'])

def sendCommand(slave, cmd, data):
        status = 0
        check = -1
        while status != 1:
                status = writeData(LAMP_ADDRESS, cmd, data)
                if status == -1:
                        return -1
                #error handling
        while int(check) != int(data):
                check = readData(LAMP_ADDRESS, 2)
                if check == -1:
                        return -1
        return 1

while True:
	index = random.randint(0, 9)
        next_cmd = cmd[index]
	if next_cmd == 'c':
		number = random.randint(0,255)
	else:
		number = random.randint(0,9999)

        status = 0
        store = -1
        original_cmd = 'z'
        error = False
        while status != 1:
                print("NUMBER: " + str(number))
                status = sendCommand(LAMP_ADDRESS, next_cmd, int(number))
                print("STATUS: " + str(status))

                if status == -1 and error == False:
                        print("ERROR")
                        store = number
                        number = 0
                        original_cmd = next_cmd
                        next_cmd = 'e'
                        error = True
                if status == 1 and error == True:
                        print("RESOLVED")
                        number = store
                        next_cmd = original_cmd
                        error = False
                        status = 0

	time.sleep(2)
