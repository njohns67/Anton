import miscFunctions as mf
import time

class Command:
	def __init__(self, anton, transcript):
		self.anton = anton
		self.transcript = transcript
		self.splitTranscript = self.transcript.split()
		self.date = mf.speechToDate(self.transcript)
		self.delayCommand = False
		self.delaySeconds = mf.subtractTimes(time)
		self.nums = []
		self.weatherDayArray = ["monday", "tuesday", "wednesday", "thursday", "friday", 
								"saturday", "sunday", "today", "tomorrow"]
		self.command = self.ret
		self.args = []
		self.commands = {"feed": wifiDevices.feedScout, "scout": wifiDevices.feedScout, 
						 "joke": APICalls.playJoke, "weather": self.getWeather, "pause": self.pauseMedia, 
						 "play": self.playMedia, "skip": self.anton.isPlaying.skipSong, "volume": self.changeVolume,
						 "beer": wifiDevices.beerMe, "alarm": self.createAlarm, "reminder": self.createAlarm, 
						 "timer": self.createAlarm, "remind": self.createAlarm, "calendar": self.createAlarm, 
						 "pray": self.playMedia, "go back": self.anton.isPlaying.previousSong, 
						 "previous": self.anton.isPlaying.previousSong, "mute": self.muteMedia,
						 "unmute": self.unMuteMedia, "un-mute": self.unMuteMedia, 
						 "silent": self.anton.changeMuteMode, "tv": self.anton.roku.rokuControl, "launch": self.launchApp, 
						 "open": self.launchApp, "watch": self.launchApp, "type": self.typeString, 
						 "heat": self.anton.thermostat.changeMode, "ac": self.anton.thermostat.changeMode, 
						 "a/c": self.anton.thermostat.changeMode,"oven": self.ovenControl, 
						 "control": self.anton.roku.rokuControl, "roku": self.anton.roku.rokuControl,
						 "nevermind": self.ret, "never-mind": self.ret, "exit": self.exit}
		
		self.dingDelays =  {"feed": False, "scout": False, 
							"joke": True, "weather": True, "pause": False, 
							"play": False, "skip": False, "volume": False,
							"beer": False, "alarm": False, "reminder": False, 
							"timer": False, "remind": False, "calendar": False, 
							"pray": True, "go back": False, 
							"previous": False, "mute": False,
							"unmute": False, "un-mute": False, 
							"silent": False, "tv": False, "launch": True, 
							"open": True, "watch": True, "type": True, 
							"heat": False, "ac": False, 
							"a/c": False,"oven": True, 
							"control": False, "roku": False,
							"nevermind": True, "never-mind": True, "exit": False}
		
		self.command = self.setCommand()
		if self.delayCommand and "weather" not in transcript:
			self.threadCommand()
			return 
		else:
			return self.command()

	def setCommand(self):
		for word in self.transcript.split():
			try:
				command = self.commands[word]
				self.playDing(dingDelays[word])
				return command
			except:
				continue
		return self.commands["nevermind"]

	def setInfo(self):
		if "on" in self.splitTranscript:
			self.on = 1
		if "off" in self.splitTranscript:
			self.on = 0
		elif "off" not in self.splitTranscript and "on" not in self.splitTranscript:
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

	def threadCommand(self):
		def delayCommand():
			time.sleep(self.delay)
			self.command(*self.args)
		thread = Thread(target=delayCommand)
		thread.daemon = True
		thread.start()

	def playDing(self, delay=False):
		if not self.bellsOff:
			p = Popen(["play", self.anton.filePaths["ding"]], stdout=PIPE, stderr=PIPE)
			if delay:
				self.anton.processes.append(p)
			else:
				p.wait()

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
		APICalls.getForecast(city, day)
		return

	def pauseMedia(self):
		if self.anton.isPlaying == self.anton.roku:
			self.anton.continuePlaying = 0
			self.anton.isPlaying.pause()
		else:
			self.anton.continuePlaying = 0
	
	def playMedia(self):
		if (len(self.self.splitTranscript) < 4 and "continue" in self.transcript) or "play the music" == self.transcript or "continue playing" in self.transcript or "play" == self.transcript:
			print("resuming")
			self.anton.continuePlaying = 1
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
				self.anton.tts("Playing " + show + " season " + str(season) + " on " + channel)
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
		if "mode" in self.splitTranscript:
			if "on" in self.splitTranscript:
				self.anton.changeMuteMode(True)
			elif "off" in self.splitTranscript:
				self.anton.changeMuteMode(False)
		else:
			self.anton.isPlaying.mute()

	def unMuteMedia(self):
		if "mode" in self.splitTranscript:
			self.anton.chamgeMuteMode(False)
		else:
			self.anton.isPlaying.unMute()
	
	def changeVolume(self):
		volume = -1
		for word in splitTranscript:
			volume = mf.wordToNum(word)
			if volume != -1:
				break
		if "up" in transcript:
			if volume == -1:
				volume = 2
			self.anton.play("VolumeUp")
			self.anton.isPlaying.volumeUp(volume)
		elif "down" in transcript:
			if volume == -1:
				volume = 2
			self.anton.play("VolumeDown")
			self.anton.isPlaying.volumeDown(volume)
		elif volume != -1:
			if volume == -1:
				volume = 2
			self.anton.isPlaying.setVolume(volume)
		else:
			self.anton.play("VolumeUpOrDown")
			self.anton.isResponding = 1
			transcript = self.anton.record().lower()
			if "up" in transcript:
				self.anton.isPlaying.volumeUp(volume)
			elif "down" in transcript:
				self.anton.isPlaying.volumeDown(volume)
			else:
				return -1

	def launchApp(self):
		if "hulu" in self.splitTranscript:
			self.anton.roku.launchApp("hulu")
		elif "netflix" in self.splitTranscript:
			self.anton.roku.launchApp("netflix")
	
	def typeString(self):
		s = self.splitTranscript[1:]
		s = " ".join(s)
		self.anton.roku.sendString(s)

	def ovenControl(self):
		if "off" in self.splitTranscript:
			self.setOven(0)
			return
		temp = 0
		for word in self.splitTranscript:
			try:
				temp = int(word)
			except:
				continue
		if temp == 0:
			try:
				toIndex = self.splitTranscript.index("to")
			except:
				return -1
			firstNum = numWords[self.splitTranscript[toIndex+1]]
			secondNum = numWords[self.splitTranscript[toIndex+2]]
			thirdNum = numWords[self.splitTranscript[toIndex+3]]
			temp = str(firstNume) + str(secondNum) + str(thirdNum)
			temp = int(temp)
		self.anton.setOven(temp)


	def ret(self):
		return

	def exit(self):
		self.anton.play("Goodbye")
		for x in self.anton.processes:
			x.send_signal(signal.SIGINT)
			x.wait()
		os.system("stty sane")
		exit(0)



