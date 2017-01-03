from time import sleep
import serial

class CheckStatus(object):
    def __init__(self):
        self.running = True
        self.listen = 0
        self.current_state = -2
        self.position = 0
        self.timer = 20
        self.status = ""
        self.atmega = serial.Serial('/dev/ttyAMA0', 57600)

    def command(self, state, value):
        send = True
        while send == True:
            print "SEND! {} {}".format(state, value)
            for letter in (state + str(value) + '\n'):
                self.atmega.write(bytes(letter.encode('ascii')))
                #sleep(0.01)
            lamp_status = self.atmega.readline()
            lamp_status = lamp_status.rstrip()
            lamp_values = lamp_status.split(":",2)
            self.status = lamp_values
            print self.status
            if lamp_values[0] == "READ":
                self.position = lamp_values[1]
                send = False
            elif lamp_values[0] == "HIGH":
                send = False
            elif lamp_values[0] == "LOW":
                send = False
            elif lamp_values[0] == "TIMER":
                if lamp_values[1] == value:
                    send = False
            elif lamp_values[0] == "ERROR":
                pass
            sleep(0.1)

    def update(self, listen, position):
        if self.listen != listen:
            self.current_state = listen
            self.listen = listen
            return self.position
        else:
            return self.position

    def stop(self):
        self.running = False

    def forever(self):
        self.running = True
        while self.running == True:
            sleep(0.1)
            if self.current_state == -1:
                print "SET LOW"
                self.command('l', 0)
                self.command('t', self.timer)
                self.current_state = -2
            elif self.current_state >= 0:
                print "SET HIGH"
                self.command('h', 180)
                self.command('t', self.timer)
                self.current_state = -2
            elif self.current_state == -2:
                self.command('r', 0)
