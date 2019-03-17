import socket
'''Functions for controlling devices on a wifi network, main
ESP8266 modules attached to servos. Not very useful unless
you've installed the necessary hardware'''

def lightOn():
    IP = "192.168.1.74"
    port = 80
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP, port))
    s.send(b"1")
    s.close()

def feedScout():
    IP = "192.168.1.76"
    port = 81
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP, port))
    s.send("1".encode())
    s.close()

def beerMe():
    IP = "192.168.1.74"
    port = 80
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP, port))
    s.send("l".encode())

def changeThermostatMode(mode):
    IP = "192.168.1.74"
    port = 80
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP, port))
    s.send(str(mode).encode())

def setOven(temp):
    IP = "192.168.1.79"
    port = 80
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP, port))
    s.send(str(temp).encode())
