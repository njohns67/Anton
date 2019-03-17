import os, subprocess

class MPC:
    '''This class controls spotify playback. All expected functions are available'''
    def __init__(self, anton):
        self.isPlaying = 0
        self.isRunning = 0
        self.anton = anton
        self.volume = 50
        p = subprocess.Popen(["amixer", "set", "Master", str(self.volume) + "%"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()

    def findSong(self, song, artist=""):
        '''Searches for a song and returns the closest match'''
        search = subprocess.check_output(["mpc", "search", "title", song, "artist", artist]).decode()
        search = search.split("\n")
        if len(search) < 1:
            return -1
        return search[0]

    def addSong(self, songID):
        '''Adds a song to the queue given a song ID'''
        subprocess.check_output(["mpc", "add", songID])

    def playSong(self, song, artist=""):
        '''Plays a given song'''
        subprocess.check_output(["mpc", "clear"])
        song = self.findSong(song, artist)
        if song == -1:
            return -1
        self.addSong(song)
        play = subprocess.check_output(["mpc", "play"]).decode()
        subprocess.check_output(["mpc", "pause"])
        play = play.split("\n")
        play = play[0].split()
        try:
            Index = play.index("-")
        except:
            play = subprocess.check_output(["mpc", "play"]).decode()
            subprocess.check_output(["mpc", "pause"])
            play = play.split("\n")
            play = play[0].split()
        p = subprocess.Popen(["mpc", "seek", "0"])
        p.wait()
        try:
            Index = play.index("-")
        except:
            return -1
        artist = " ".join(play[:Index])
        song = " ".join(play[Index+1:])
        print(song)
        print(artist)
        self.anton.isPlaying = self.anton.mpc
        self.anton.continuePlaying = 1
        self.anton.tts("Playing " + song + " by " + artist)

    def play(self):
        '''Continues playing music if music was previously playing'''
        try:
            out = subprocess.check_output(["mpc", "play"])
            out = out.split("\n")
            out.index("-")
            self.isPlaying = 1
            self.anton.isPlaying = self.anton.mpc
            self.anton.continuePlaying = 1
        except:
            return -1

    def pause(self):
        subprocess.Popen(["mpc", "pause"])
        self.isPlaying = 0

    def skip(self):
        subprocess.Popen(["mpc", "next"])

    def previous(self):
        subprocess.Popen(["mpc", "prev"])

    def queueSong(self, song, artist=""):
        songID = self.findSong(song, artist)
        if songID == -1:
            return -1
        self.addSong(songID)

    def volumeUp(self, volume=0):
        p = subprocess.Popen(["amixer", "set", "Master", "10%+"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.volume += 10
        if self.volume > 100:
            self.volume == 100

    def volumeDown(self, volume=0):
        p = subprocess.Popen(["amixer", "set", "Master", "10%-"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.volume -= 10
        if self.volume < 0:
            self.volume = 0

    def mute(self):
        p = subprocess.Popen(["amixer", "set", "Master", "0%"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def setVolume(self, volume):
        volume *= volume
        self.anton.tts("Setting the volume to " + str(volume))
        p = subprocess.Popen(["amixer", "set", "Master", str(volume) + "%"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        self.volume = volume

    def unMute(self):
        self.setVolume(self.volume)

