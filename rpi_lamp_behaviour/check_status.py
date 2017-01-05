from time import sleep
import serial

class CheckStatus(object):
    def __init__(self):
        self.running = True
        self.listen = 0
        self.current_state = -2
        self.position = 0
        self.read = True
        self.cmd = 'r'
        self.value = 0
        self.status = ""
        self.atmega = serial.Serial('/dev/ttyAMA0', 57600)

    def command(self, state, value):
        for letter in (state + str(value)):
            self.atmega.write(bytes(letter.encode('ascii')))
            #sleep(0.01)
        try:
            lamp_status = self.atmega.readline()
            self.atmega.flushInput()
        except Exception as e:
            self.atmega.flushInput()
            return False
        lamp_status = lamp_status.rstrip()
        lamp_values = lamp_status.split(":",2)
        self.status = lamp_values
        #print self.status
        if state == 'r' and lamp_values[0] == "READ":
            self.position = lamp_values[1]
            return True
        elif state == 'h' and lamp_values[0] == "HIGH":
            return True
        elif state == 'l' and lamp_values[0] == "LOW":
            return True
        elif state == 't' and lamp_values[0] == "TIMER":
            if lamp_values[1] == value:
                return True
            else:
                return False
        elif lamp_values[0] == "ERROR":
            return False
        else:
            return False

    def update(self, cmd, value):
        self.read = False
        sleep(0.1)
        while self.read == False:
            self.read = self.command(cmd, value)
            sleep(0.1)

    def stop(self):
        self.running = False

    def forever(self):
        self.running = True
        while self.running == True:
            sleep(0.1)
            if self.read == True:
                self.command('r', 0)
            else:
                pass
