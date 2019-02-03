from time import sleep
import serial, os, signal
from subprocess import Popen, PIPE
import random

todayWeatherArrays = [["todays", "weather"], ["today", "weather"], ["today's", "weather"], ["the weather in"]]
tomWeatherArrays = [["tomorrow", "weather"], ["tomorrows", "weather"], ["tomorrow's", "weather"]]
commandArray = ["joke", "weather", "alarm", "play", "next", 
                "pause", "volume", "skip", "feed", "beer", "exit", "scout"]
weatherDayArray = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "today", "tomorrow"]
questionArray = ["who", "whose", "who's", "whos", 
                 "what", "what's", "whats", 
                 "when", "when's", "whens", 
                 "where", "where's", "wheres", 
                 "why", "why's", "whys",
                 "how", "how's", "hows"]
numWords = {"mute": 0, "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, 
            "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}

def playDingDelay(self):
    if not self.bellsOff:
        p = Popen(["play", self.filePaths["ding"]], stdout=PIPE, stderr=PIPE)
        self.processes.append(p)

def playDing(self):
    if not self.bellsOff:
        p = Popen(["play", self.filePaths["ding"]], stdout=PIPE, stderr=PIPE)
        p.wait()

def parse(self, transcript):
    transcript = transcript.lower()
    splitTranscript = transcript.split()
    if "joke" in transcript:
        playDingDelay(self)
        self.getJoke()

    elif "weather" in transcript:
        playDingDelay(self)
        city = ""
        splitTranscript = transcript.split()
        day = ""
        both = set(weatherDayArray).intersection(splitTranscript)
        if len(both) == 0:
            day = "today"
        else:
            index = [weatherDayArray.index(x) for x in both]
            day = weatherDayArray[index[len(index)-1]]
        print(day)
        try:
            if len(both) == 0:
                index = splitTranscript.index("in")
                city = splitTranscript[index+1:]
                city = " ".join(city)
            else:
                dayIndex = splitTranscript.index(day)
                index = splitTranscript.index("in")
                if dayIndex == len(splitTranscript)-1:
                    city = splitTranscript[index+1:dayIndex]
                    city = " ".join(city)
                else:
                    city = splitTranscript[index+1:]
                    city = " ".join(city)
        except ValueError:
            city = ""
        print(city)
        self.getForecast(city, day)

    elif "alarm" in transcript or "timer" in transcript:
        playDingDelay(self)
        if not any(x in transcript for x in ["minutes", "seconds", "hours", "minute", "hour"]):
            self.play("BadTimer")
            return
        a, playString = transcript.split("for")
        splitTranscript = transcript.split()
        nums = []
        indices = []
        letters = []
        i = 0
        for x in splitTranscript:
            i += 1
            try:
               nums.append(int(x))
               indices.append(i)
            except ValueError:
                continue
        if len(nums) == 0:
            self.play("BadRec")
            return
        for x in indices:
            letters.append(splitTranscript[x][0])
        if "and a half" in transcript or "1/2" in transcript:
            nums.append(30)
            if letters[0] == 'm':
                letters.append('s')
            else:
                letters.append('m')
        try:
            if len(nums) == 1:
                p = Popen(["/home/pi/Anton/Resources/timer", str(nums[0]), letters[0]])
                self.processes.append(p)
            else:
                p = Popen(["/home/pi/Anton/Resources/timer", str(nums[0]), letters[0], str(nums[1]), letters[1]])
                self.processes.append(p)
        except Exception as e:
            print(e)
            self.play("BadRec")
        self.tts("I've set your timer for" + playString)

    elif "play" in transcript or "pray" in transcript or "playing" in transcript:
        if (len(splitTranscript) < 4 and "continue" in transcript) or "play the music" == transcript or "continue playing" in transcript or "play" == transcript:
            print("resuming")
            self.continuePlaying = 1
            if self.isPlaying == None:
                if any(x in transcript for x in ["tv", "t.v.", "television", "hulu", "netflix"]):
                    self.isPlaying = self.roku
                elif "music" in transcript:
                    self.isPlaying = self.mpc
                elif "pandora" in transcript:
                    self.isPlaying = self.pandora
                self.play("WhatPlay")
                self.isResponding = 1
                transcript = self.record()
                print(transcript)
                transcript = transcript.lower()
                if any(x in transcript for x in ["tv", "t.v.", "television", "hulu", "netflix"]):
                    self.isPlaying = self.roku
                elif "music" in transcript:
                    self.isPlaying = self.mpc
                elif "pandora" in transcript:
                    self.isPlaying = self.pandora
            return
        if any(x in transcript for x in ["netflix", "hulu", "amazon", "prime"]):
            playDing(self)
            if "on" not in transcript:
                self.playSound("BadRoku")
                return
            Index = splitTranscript.index("play")
            onIndex = splitTranscript.index("on")
            show = splitTranscript[Index+1:onIndex]
            channel = splitTranscript[onIndex+1:]
            show = " ".join(show)
            channel = " ".join(channel)
            if "season" in transcript:
                Index = splitTranscript.index("season")
                season = splitTranscript[Index+1]
                try:
                    season = int(season)
                except:
                    season = numWords[season]
                self.tts("Playing " + show + " season " + str(season) + " on " + channel)
                self.playShow(show=show, channel=channel, season=season)
                return
            self.tts("Playing " + show + " on " + channel)
            print(show)
            print(channel)
            self.playShow(show=show, channel=channel)
            return
        elif "pandora" in transcript or "radio" in transcript:
            playDing(self)
            if "radio" in transcript:
                Index = splitTranscript.index("radio") + 1
            else:
                Index = splitTranscript.index("pandora")
                if splitTranscript[Index-1] == "on":
                    Index -= 1
            playIndex = splitTranscript.index("play")
            station = splitTranscript[playIndex+1:Index]
            station = " ".join(station)
            self.pandora.changeStation(station)
            print(station)
            return 0
        else:
            playDing(self)
            transcript = transcript
            splitTranscript = transcript.split()
            index = splitTranscript.index("play")
            index2 = 0
            try:
                index2 = splitTranscript.index("by")
            except ValueError:
                song = ""
                if "next" in transcript or "after this" in transcript:
                    for x in range(index+1, len(splitTranscript)-1):
                        song += splitTranscript[x]
                        song += " "
                    songInfo = self.mpc.queueSong(song)
                    if songInfo == -1:
                        self.play("BadSong")
                        return -1
                    return
                else:
                    for x in range(index+1, len(splitTranscript)):
                        song += splitTranscript[x]
                        song += " "
                    songInfo = self.mpc.playSong(song)
                    if songInfo == -1:
                        self.play("BadSong")
                        return -1
                    return
            song = ""
            artist = ""
            if "next" in transcript or "after this" in transcript:
                for x in range(index+1, index2):
                    song += splitTranscript[x]
                    song += " "
                for x in range(index2+1, len(splitTranscript)-1):
                    artist += splitTranscript[x]
                    artist += " "
                print(song)
                print(artist)
                songInfo = self.mpc.queueSong(song)
                if songInfo == -1:
                    self.play("BadSong")
                    return -1
                return
            else:
                for x in range(index+1, index2):
                    song += splitTranscript[x]
                    song += " "
                for x in range(index2+1, len(splitTranscript)):
                    artist += splitTranscript[x]
                    artist += " "
                print(song)
                print(artist)
                songInfo = self.mpc.playSong(song, artist=artist)
                if songInfo == -1:
                    self.play("BadSong")
                    return -1
                self.isPlaying = self.mpc
                return

    elif "pause" in transcript or ("stop" in transcript and "music" in transcript) or "show" in transcript:
        playDing(self)
        if self.isPlaying != None:
            self.isPlaying.pause()
            self.continuePlaying = 0
        else:
            self.isPlaying = self.roku
            self.isPlaying.pause()
            self.continuePlaying = 0
            return

    elif "volume" in transcript:
        playDing(self)
        splitTranscript = transcript.split()
        volume = -1
        for word in transcript:
            try:
                volume = numWords[word]
            except:
                pass
            try:
                volume = int(word)
            except:
                continue
        print(str(volume))
        if volume != -1:
            self.tts("Setting the volume to " + str(volume))
            volume *= 10
            p = Popen(["amixer", "set", "Master", str(volume) + "%"], stdout=PIPE, stderr=PIPE)
            p.wait()
            return
        if "up" in transcript:
            if self.isPlaying == None:
                if "tv" in transcript or "television" in transcript or "t.v" in transcript or "hulu" in transcript or "netflix" in transcript:
                    self.roku.volumeUp(2)
                    self.isPlaying = self.roku
                    return
                elif "pandora" in transcript or "music" in transcript:
                    self.isPlaying = self.mpc
                    self.isPlaying.volumeUp()
                    return
                else:
                    self.play("WhatVolumeUp")
                    self.isResponding = 1
                    transcript = self.record().lower()
                    if "tv" in transcript or "television" in transcript or "t.v." in transcript:
                        print("Tv volume")
                        self.roku.volumeUp(2)
                        self.isPlaying = self.roku
                        return
                    else:
                        self.play("VolumeUp")
                        self.isPlaying = self.mpc
                        self.isPlaying.volumeUp()
                        return
            else:
                self.play("VolumeUp")
                self.isPlaying.volumeUp()
        elif "down" in transcript:
            if self.isPlaying == None:
                if "tv" in transcript or "television" in transcript or "t.v." in transcript or "hulu" in transcript or "netflix" in transcript:
                    self.isPlaying = self.roku
                    self.roku.volumeDown(2)
                    return
                elif "pandora" in transcript or "music" in transcript:
                    self.isPlaying = self.mpc
                    self.isPlaying.volumeDown()
                    return
                else:
                    self.play("WhatVolumeDown")
                    self.isResponding = 1
                    transcript = self.record().lower()
                    if "tv" in transcript or "television" in transcript or "t.v." in transcript:
                        print("Tv volume")
                        self.isPlaying = self.roku
                        self.roku.volumeDown(2)
                        return
                    else:
                        self.play("VolumeDown")
                        self.isPlaying = self.mpc
                        self.isPlaying.volumeDown()
                        return
            else:
                self.play("VolumeDown")
                self.isPlaying.volumeDown()
        else:
            #TODO: Add "Would you like the volume up or down?" response
            return

    elif "skip" in transcript:
        playDing(self)
        if self.isPlaying != None:
            self.isPlaying.skip()

    elif "go back" in transcript or "previous song" in transcript:
        playDing(self)
        self.mpc.previous()

    elif "feed" in transcript or "scout" in transcript:
        playDing(self)
        self.play("FeedingScout")
        self.feedScout()

    elif "beer" in transcript:
        playDing(self)
        self.beerMe()

    elif any(x in transcript for x in questionArray):
        playDingDelay(self)
        if self.askQuestion(transcript) == -1:
            num = random.randint(1, 5)
            file = "BadWolfram" + str(num)
            self.play(file)

    elif "mute" in transcript:
        self.play("Mute")
        self.isMuted = 1

    elif any(x in transcript for x in ["unmute", "un-mute", "volume up", "up the volume"]):
        self.play("Unmuted")
        self.isMuted = 0

    elif "silent" in transcript:
        if "toggle" in transcript:
            self.bellsOff = not self.bellsOff
        elif "on" in transcript:
            self.bellsOff = 1
        else:
            self.bellsOff = 0
            
    elif "tv" in transcript and ("off" in transcript or "on" in transcript):    
        playDing(self)
        if "hulu" in transcript:
            self.roku.launchApp("hulu")
        elif "netflix" in transcript:
            self.roku.launchApp("netflix")
        else:
            self.roku.power()

    elif ("launch" in transcript or "open" in transcript or "watch" in transcript) and ("netflix" in transcript or "hulu" in transcript):
        playDing(self)
        if "hulu" in transcript:
            self.roku.launchApp("hulu")
        elif "netflix" in transcript:
            self.roku.launchApp("netflix")
    
    elif "type" in transcript:
        s = splitTranscript[1:]
        s = " ".join(s)
        self.roku.sendString(s)

    elif "heat" in transcript and "on" in transcript:
        self.thermostat.changeMode(2)

    elif "ac" in transcript and "on" in transcript:
        self.thermostat.changeMode(1)

    elif "exit" in transcript:
        playDing(self)
        self.play("Goodbye")
        for x in self.processes:
            x.send_signal(signal.SIGINT)
            x.wait()
        os.system("stty sane")
        exit(0)
    else:
        print("I didn't quite get that. Please try again.")
        return -1
    
