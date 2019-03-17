from threading import Thread
import wifiDevices
import time
import datetime as dt
import miscFunctions as mf


class Thermostat:           #Mode 1 for cool, 2 for heat
    def __init__(self, anton, temp=70, mode=2):
        self.anton = anton
        self.temp = temp
        self.mode = mode
        self.modes = [0, 2, 1]

    def changeModeDelay(self, wallTime, mode):
        wallTime = mf.subtractTimes(wallTime)
        def countdown():
            print("Sleeping")
            time.sleep(wallTime)
            self.changeMode(mode)
            print("Changing")
        thread = Thread(target=countdown)
        thread.daemon = True
        thread.start()

    def changeMode(self, mode=3):
        if mode == 3:
            mode = self.modes[self.mode]
        wifiDevices.changeThermostatMode(mode)
        self.mode = mode

