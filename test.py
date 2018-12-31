import serial

s = serial.Serial(port="/dev/ttyUSB0", baudrate=9600)
while 1:
    temp = input("Enter num ")
    print(type(temp))
    s.write(temp.encode())
