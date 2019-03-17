import datetime as dt
import APICalls
import time
import json
import miscFunctions as mf
import sounds
from threading import Thread

class Clock:
    def __init__(self):
        self.allClasses = []
        self.jsonFile = "/home/pi/Anton/Resources/clocks.json"
        self.numReminders = 0
    
    def importData(self):
        with open(self.jsonFile) as jsonFile:
            data = json.load(jsonFile)
            for x in data:
                if x["type"] == "reminder":
                    self.allClasses.append(Reminder(x["dateTime"], x["message"]))
                    self.numReminders += 1
                elif x["type"] == "alarm":
                    self.allClasses.append(Alarm(x["dateTime"], x["sound"]))
                elif x["type"] == "timer":
                    self.allClasses.append(Timer(x["dateTime"], x["sound"]))

    def dumpData(self):
        with open(self.jsonFile) as jsonFile:
            json.dump(self.allClasses, jsonFile)

    def createAlarm(self, dateTime, sound="/home/pi/Anton/Sounds/alert.wav"):
        alarm = Alarm(dateTime, sound)
        self.startTimer(alarm)
        return

    def createTimer(self, dateTime, sound="/home/pi/Anton/Sounds/alert.wav"):
        timer = Timer(dateTime, sound)
        self.startTimer(timer)
        return

    def createReminder(self, dateTime, message):
        self.numReminders += 1
        reminder = Reminder(dateTime, message, self.numReminders)
        self.startTimer(reminder)
        return
    
    def startTimer(self, timer):
        def f(self, timer):
            time.sleep(timer.seconds)
            timer.playSound()
            timer.playMessage()
            self.allClasses.remove(timer)
            if type(timer) == Reminder:
                self.numReminders -= 1
        thread = Thread(target=f, args=[self, timer])
        thread.daemon = True
        thread.start()
        self.allClasses.append(timer)
        

class Alarm:
    def __init__(self, dateTime, sound="/home/pi/Anton/Sounds/alert.wav"):
        self.sound = sound
        self.dateTime = dateTime
        self.seconds = mf.subtractTimes(dateTime)

    def playSound(self):
        sounds.playSound(self.sound)

    def playMessage(self):
        pass

class Reminder:
    def __init__(self, dateTime, message, responseID):
        self.message = message
        self.dateTime = dateTime
        self.seconds = mf.subtractTimes(dateTime)
        APICalls.tts(message, "/home/pi/Anton/Reminders/ReminderMessage"+str(responseID))
        self.message = "/home/pi/Anton/Reminders/ReminderMessage" + str(responseID) + ".mp3"
    
    def playSound(self):
        pass

    def playMessage(self):
        sounds.playSound(self.message)

class Timer:
    def __init__(self, dateTime, sound="/home/pi/Anton/Sounds/alert.wav"):
        self.sound = sound
        self.dateTime = dateTime
        self.seconds = mf.subtractTimes(dateTime)
    
    def playSound(self):
        sounds.playSound(self.sound)

    def playMessage(self):
        pass

