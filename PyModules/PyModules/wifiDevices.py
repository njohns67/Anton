import socket

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
