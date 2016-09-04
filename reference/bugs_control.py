# Bugs control program (Client, Server, Microcontroller)
import zmq
from time import sleep
import json
import smbus
from multiprocessing import Process, Pipe

# server Process
def lamp_server(connect):
    # SERVER
    server_context = zmq.Context()
    server = server_context.socket(zmq.PUB)
    server.connect("tcp://armadillo.local:8101")
    #socket.connect("tcp://bison.local:8101")

    while True:
        update = json.loads(connect.recv())
        update = json.dumps({"lamp": update["lamp"], "zipcode": update["zipcode"]}, sort_keys=True)
        server.send_json(update)
        print(update)
        sleep(0.01)

# microcontroller i2c communication


def update_lamp(update):
    lamp = update["lamp"] + 1
    zcode = update["zipcode"] + 1
    lamp_status = json.dumps({"lamp": lamp, "zipcode": zcode}, sort_keys=True)
    return lamp_status

def main():
    # CLIENT
    client_context = zmq.Context()
    client = client_context.socket(zmq.SUB)
    client.connect("tcp://armadillo.local:8100")
    #client.connect("tcp://bison.local:8101")
    client.setsockopt(zmq.SUBSCRIBE, b'')

    #LAMP VARIABLES
    my_lamp = 0
    zcode = 0
    lamp_status = json.dumps({"lamp": 0, "zipcode": 0})

    main_connection, server_connection = Pipe()
    main_connection.send(lamp_status)
    server_process = Process(target=lamp_server, args=(server_connection,))
    server_process.start()

    while True: 
        lamp_status = update_lamp(json.loads(client.recv_json()))
        main_connection.send(lamp_status)

if __name__ == '__main__':
    main()