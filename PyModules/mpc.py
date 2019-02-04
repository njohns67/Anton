import subprocess, os

class MPC:
    def __init__(self, anton):
        self.isPlaying = 0
        self.isRunning = 0
        self.anton = anton

    def findSong(self, song, artist=""):
        search = subprocess.check_output(["mpc", "search", "title", song, "artist", artist]).decode()
        search = search.split("\n")
        if len(search) < 1:
            return -1
        return search[0]

    def addSong(self, songID):
        subprocess.check_output(["mpc", "add", songID])

    def playSong(self, song, artist=""):
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

    def prev(self):
        subprocess.Popen(["mpc", "prev"])

    def queueSong(self, song, artist=""):
        songID = self.findSong(song, artist)
        if songID == -1:
            return -1
        self.addSong(songID)

    def volumeUp(self):
        p = subprocess.Popen(["amixer", "set", "Master", "10%+"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def volumeDown(self):
        p = subprocess.Popen(["amixer", "set", "Master", "10%-"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
