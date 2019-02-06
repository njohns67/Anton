import miscFunctions as mf
import time

class Command:
    def __init__(self, anton, transcript):
        self.anton = anton
        self.transcript = transcript
        self.splitTranscript = self.transcript.split()
        self.date = mf.speechToDate(self.transcript)
        self.delayCommand = 0
        self.delaySeconds = mf.subtractTimes(time)
        self.nums = []
        self.weatherDayArray = ["monday", "tuesday", "wednesday", "thursday", "friday", 
                                "saturday", "sunday", "today", "tomorrow"]
        self.command = None
        self.commands = {"feed": wifiDevices.feedScout, "scout": wifiDevices.feedScout, 
                         "joke": APICalls.playJoke, "weather": self.getWeather, "pause": self.pauseMedia, 
                         "play": self.playMedia, "skip": self.anton.isPlaying.skipSong, "volume": changeVolume,
                         "beer": wifiDevices.beerMe, "alarm": self.createAlarm, "reminder": self.createAlarm, 
                         "timer": self.createAlarm, "pray": playMedia, 
                         "go back": self.anton.isPlaying.previousSong, 
                         "previous": self.anton.isPlaying.previousSong, "mute": self.muteMedia,
                         "unmute": self.unMuteMedia, "un-mute": self.unMuteMedia, 
                         "silent": self.anton.changeMuteMode, "tv": self.controlTV, "launch": self.launchApp, 
                         "open": self.launchApp, "watch": self.launchApp, "type": self.typeString, 
                         "heat": self.anton.thermostat.changeMode, "ac": self.anton.thermostat.changeMode, 
                         "oven": self.ovenControl, "control": self.anton.roku.rokuControl, 
                         "roku": self.anton.roku.rokuControl, "nevermind": self.ret, "exit", self.exit}
        self.args = []
        self.command()

    def setCommand(self):
        for word in self.transcript.split():
            try:
                return self.commands[word]
            except:
                continue
        return self.commands["nevermind"]

    def setInfo(self):
        if "on" in self.transcript:
            self.on = 1
        if "off" in self.transcript:
            self.on = 0
        elif "off" not in self.transcript and "on" not in self.transcript:
            self.on = None
        date = mf.speechToDate(self.transcript)
        if date:
            self.date = date
            self.delayCommand = 1
            self.delaySeconds = mf.subtractTimes(time)
        else:
            self.date = 0
            self.delayCommand = 0
            self.delaySeconds = 0
        self.nums.append(mf.wordToNum(word) for word in self.transcript.split() if mf.wordToNum(word) != -1) 

    def delayCommand(self):
        thread = Thread(target=self.threadCommand)
        thread.daemon = True
        thread.start()

    def threadCommand(self):
        time.sleep(self.delay)
        self.command(*self.args)

    def getWeather(self):
        city = ""
        self.splitTranscript = self.transcript.split()
        day = ""
        both = set(self.weatherDayArray).intersection(self.splitTranscript)
        if len(both) == 0:
            day = "today"
        else:
            index = [self.weatherDayArray.index(x) for x in both]
            day = self.weatherDayArray[index[len(index)-1]]
        print(day)
        try:
            if len(both) == 0:
                index = self.splitTranscript.index("in")
                city = self.splitTranscript[index+1:]
                city = " ".join(city)
            else:
                dayIndex = self.splitTranscript.index(day)
                index = self.splitTranscript.index("in")
                if dayIndex == len(self.splitTranscript)-1:
                    city = self.splitTranscript[index+1:dayIndex]
                    city = " ".join(city)
                else:
                    city = self.splitTranscript[index+1:]
                    city = " ".join(city)
        except ValueError:
            city = ""
        print(city)
        self.getForecast(city, day)
        pass

    def pauseMedia(self):
        pass
    
    def playMedia(self):
        if (len(self.self.splitTranscript) < 4 and "continue" in self.transcript) or "play the music" == self.transcript or "continue playing" in self.transcript or "play" == self.transcript:
            print("resuming")
            self.anton.continuePlaying = 1
            if self.anton.isPlaying == None:
                self.anton.setIsPlaying()
            return
        if any(x in self.transcript for x in ["netflix", "hulu", "amazon", "prime"]):
            if "on" not in self.transcript:
                self.playSound("BadRoku")
                return
            Index = self.splitTranscript.index("play")
            onIndex = self.splitTranscript.index("on")
            show = self.splitTranscript[Index+1:onIndex]
            channel = self.splitTranscript[onIndex+1:]
            show = " ".join(show)
            channel = " ".join(channel)
            if "season" in self.transcript:
                Index = self.splitTranscript.index("season")
                season = self.splitTranscript[Index+1]
                try:
                    season = int(season)
                except:
                    season = numWords[season]
                self.tts("Playing " + show + " season " + str(season) + " on " + channel)
                self.anton.roku.playShow(show=show, channel=channel, season=season)
                return
            self.anton.tts("Playing " + show + " on " + channel)
            print(show)
            print(channel)
            self.anton.roku.playShow(show=show, channel=channel)
            return
        elif "pandora" in self.transcript or "radio" in self.transcript:
            if "radio" in self.transcript:
                Index = self.splitTranscript.index("radio") + 1
            else:
                Index = self.splitTranscript.index("pandora")
                if self.splitTranscript[Index-1] == "on":
                    Index -= 1
            playIndex = self.splitTranscript.index("play")
            station = self.splitTranscript[playIndex+1:Index]
            station = " ".join(station)
            self.anton.pandora.changeStation(station)
            print(station)
            return 0
        else:
            self.transcript = self.transcript
            self.splitTranscript = self.transcript.split()
            index = self.splitTranscript.index("play")
            index2 = 0
            try:
                index2 = self.splitTranscript.index("by")
            except ValueError:
                song = ""
                if "next" in self.transcript or "after this" in self.transcript:
                    for x in range(index+1, len(self.splitTranscript)-1):
                        song += self.splitTranscript[x]
                        song += " "
                    songInfo = self.anton.mpc.queueSong(song)
                    if songInfo == -1:
                        self.play("BadSong")
                        return -1
                    return
                else:
                    for x in range(index+1, len(self.splitTranscript)):
                        song += self.splitTranscript[x]
                        song += " "
                    songInfo = self.anton.mpc.playSong(song)
                    if songInfo == -1:
                        self.play("BadSong")
                        return -1
                    return
            song = ""
            artist = ""
            if "next" in self.transcript or "after this" in self.transcript:
                for x in range(index+1, index2):
                    song += self.splitTranscript[x]
                    song += " "
                for x in range(index2+1, len(self.splitTranscript)-1):
                    artist += self.splitTranscript[x]
                    artist += " "
                print(song)
                print(artist)
                songInfo = self.anton.mpc.queueSong(song)
                if songInfo == -1:
                    self.play("BadSong")
                    return -1
                return
            else:
                for x in range(index+1, index2):
                    song += self.splitTranscript[x]
                    song += " "
                for x in range(index2+1, len(self.splitTranscript)):
                    artist += self.splitTranscript[x]
                    artist += " "
                print(song)
                print(artist)
                songInfo = self.anton.mpc.playSong(song, artist=artist)
                if songInfo == -1:
                    self.play("BadSong")
                    return -1
                self.anton.isPlaying = self.anton.mpc
                return

    def muteMedia(self):
        pass

    def unMuteMedia(self):
        pass

    def launchApp(self):
        pass
    
    def typeString(self):
        pass

    def ovenControl(self):
        pass

    def ret(self):
        return

    def exit(self):
        pass



