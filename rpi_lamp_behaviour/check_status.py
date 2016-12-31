from time import sleep
import serial

class CheckStatus(object):
    def __init__(self):
        self.running = True
        self.listen = 0
        self.position = 0
        self.status = ""
        self.atmega = serial.Serial('/dev/ttyAMA0', 57600)

    def set(self):
        send = 't' + str(self.position)
        for letter in send:
            self.atmega.write(bytes(letter.encode('ascii')))
            #sleep(0.01)
        lamp_status = self.atmega.readline()
        lamp_status = lamp_status.rstrip()
        lamp_values = lamp_status.split(":",2)
        self.status = lamp_values

    def get(self):
        send = 'r'
        for letter in send:
            self.atmega.write(bytes(letter.encode('ascii')))
        lamp_status = self.atmega.readline()
        lamp_status = lamp_status.rstrip()
        lamp_values = lamp_status.split(":",2)
        self.status = lamp_values
        if lamp_values[0] == "dial":
            self.position = lamp_values[1]

    def update(self, listen, position):
        self.listen = listen
        if listen == -1:
            return self.position
        elif listen >= 0:

            self.position = position
            return self.position

    def stop(self):
        self.running = False

    def forever(self):
        self.running = True
        while self.running == True:
            sleep(0.1)
            if self.listen == -1:
                self.get()
            elif self.listen >= 0:
                self.set()
