from time import sleep
import datetime as dt
import json
import miscFunctions as mf

class Clock:
    def __init__(self, anton):
        self.alarms = None
        self.timers = None
        self.reminders = None

    def importData(self, path="/home/pi/Anton/Resources/clocks.json"):
        return

    def createAlert(self, message="alert.wav", date):
        return

    def createAlarm(self, date):
        return

    def createTimer(self, date):
        return

    def createReminder(self, date, message):
        return

        


