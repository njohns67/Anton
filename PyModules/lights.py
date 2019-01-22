from pixel_ring import pixel_ring as pr
from gpiozero import LED
from threading import Thread

class Lights(Anton):
    def __init__(self):
        pwoer = LED(5)
        power.on()
        pr.set_brightness(100)
        self.thread = Thread(target=lightThread)
        self.thread.start()

    def lightOn(self):
        pr.set_color_delay(r=0, g=0, b=255, delay=.02)

    def lightSuccess(self):
        pr.set_color(r=0, g=255, b=0)

    def lightFail(self):
        pr.set_color(r=255, g=0, b=0)
        time.sleep(1)
        lightOff()

    def lightOff(self):
        pr.turn_off_color_delay(delay=.02)

    def lightThread(self):
        while self.isDead != True:
            if self.isRecording:
                self.lightOn()
            elif self.isParsed:
                self.lightSuccess()
            elif self.badTranscript:
                self.lightFail()
            elif not self.isRecording:
                lightOff()
            else:
                pass
