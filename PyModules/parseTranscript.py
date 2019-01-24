from time import sleep
import serial, os, signal
from subprocess import Popen, PIPE
import random

directory = "/home/pi/Anton/Responses/"

todayWeatherArrays = [["todays", "weather"], ["today", "weather"], ["today's", "weather"], ["the weather in"]]
tomWeatherArrays = [["tomorrow", "weather"], ["tomorrows", "weather"], ["tomorrow's", "weather"]]
commandArray = ["light", "joke", "weather", "alarm", "play", "next", 
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
    print(transcript)
    if "joke" in transcript:
        playDingDelay(self)
        self.getJoke()

    elif "weather" in transcript:
        playDingDelay(self)
        city = ""
        transcript2 = transcript.split()
        day = ""
        both = set(weatherDayArray).intersection(transcript2)
        if len(both) == 0:
            day = "today"
        else:
            index = [weatherDayArray.index(x) for x in both]
            day = weatherDayArray[index[len(index)-1]]
        print(day)
        try:
            if len(both) == 0:
                index = transcript2.index("in")
                city = transcript2[index+1:]
                city = " ".join(city)
            else:
                dayIndex = transcript2.index(day)
                index = transcript2.index("in")
                if dayIndex == len(transcript2)-1:
                    city = transcript2[index+1:dayIndex]
                    city = " ".join(city)
                else:
                    city = transcript2[index+1:]
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
        transcript2 = transcript.split()
        nums = []
        indices = []
        letters = []
        i = 0
        for x in transcript2:
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
            letters.append(transcript2[x][0])
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
        if any(x in transcript for x in ["netflix", "hulu", "amazon", "prime"]):
            playDing(self)
            if "on" not in transcript:
                self.playSound("BadRoku")
                return
            splitTranscript = transcript.split()
            Index = splitTranscript.index("play")
            onIndex = splitTranscript.index("on")
            show = splitTranscript[Index+1:onIndex]
            channel = splitTranscript[onIndex+1:]
            show = " ".join(show)
            channel = " ".join(channel)
            if "season" in splitTranscript:
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
        if any(x in transcript for x in ["tv", "T.V.", "television", "show", "t.v."]):
            playDing(self)
            self.roku.togglePlay()
            return
        self.isPlaying = 1
        playDing(self)
        transcript2 = transcript
        transcript = transcript.split()
        if (len(transcript) < 4 and "continue" in transcript) or "play the music" == transcript2 or "continue playing" in transcript2 or "play" == transcript2:
            print("resuming")
            return 3
        index = transcript.index("play")
        index2 = 0
        try:
            index2 = transcript.index("by")
        except ValueError:
            song = ""
            if "next" in transcript or "after this" in transcript2:
                for x in range(index+1, len(transcript)-1):
                    song += transcript[x]
                    song += " "
                songInfo = self.mpc.queueSong(song)
                if songInfo == -1:
                    self.playSound("BadSong")
                    return -1
                self.tts("Added " + songInfo[0] + " by " + songInfo[1] + " to the queue")
                return 3
            else:
                for x in range(index+1, len(transcript)):
                    song += transcript[x]
                    song += " "
                songInfo = self.mpc.playSong(song)
                if songInfo == -1:
                    self.playSound("BadSong")
                    return -1
                self.tts("Playing " + songInfo[0] + " by " + songInfo[1])
                return 3
        song = ""
        artist = ""
        if "next" in transcript or "after this" in transcript2:
            for x in range(index+1, index2):
                song += transcript[x]
                song += " "
            for x in range(index2+1, len(transcript)-1):
                artist += transcript[x]
                artist += " "
            print(song)
            print(artist)
            songInfo = self.mpc.queueSong(song)
            if songInfo == -1:
                self.playSound("BadSong")
                return -1
            song = songInfo[0]
            artist = songInfo[1]
            self.tts("Added " + song + " by " + artist + " to the queue")
            return 3
        else:
            for x in range(index+1, index2):
                song += transcript[x]
                song += " "
            for x in range(index2+1, len(transcript)):
                artist += transcript[x]
                artist += " "
            print(song)
            print(artist)
            songInfo = self.mpc.playSong(song)
            if songInfo == -1:
                self.playSound("BadSong")
                return -1
            self.tts("Playing " + songInfo[0] + " by " + songInfo[1])
            return 3

    elif "pause" in transcript or ("stop" in transcript and "music" in transcript) or "show" in transcript:
        playDing(self)
        if any(x in transcript for x in ["tv", "T.V.", "television", "show", "t.v."]):
            self.roku.togglePlay()
            return
        self.isPlaying = 0
        print("Pausing music")
        return 2

    elif "volume" in transcript:
        playDing(self)
        splitTranscript = transcript.split()
        volume = -1
        for word in splitTranscript:
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
            self.play("VolumeUp")
            p = Popen(["amixer", "set", "Master", "10%+"], stdout=PIPE, stderr=PIPE)
        elif "down" in transcript:
            self.play("VolumeDown")
            p = Popen(["amixer", "set", "Master", "10%-"], stdout=PIPE, stderr=PIPE)
        else:
            #TODO: Add "Would you like the volume up or down?" response
            return

    elif "skip" in transcript:
        playDing(self)
        self.mpc.skip()

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
            
    elif "tv" in transcript or "t.v." in transcript or "turn off" in transcript:
        playDing(self)
        self.roku.power()


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
    
