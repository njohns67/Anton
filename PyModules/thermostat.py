from threading import Thread
import wifiDevices
import time as T
import datetime as dt
import miscFunctions as mf


class Thermostat:           #Mode 1 for cool, 2 for heat
    def __init__(self, anton, temp=70, mode=1):
        self.anton = anton
        self.temp = temp
        self.mode = mode

    def changeModeDelay(self, time, mode):
        time = mf.subtractTimes(time)
        def countdown():
            print("Sleeping")
            T.sleep(time)
            self.changeMode(mode)
            print("Changing")
        thread = Thread(target=countdown)
        thread.daemon = True
        thread.start()

    def changeMode(self, mode):
        wifiDevices.changeThermostatMode(mode)
        self.mode = mode

