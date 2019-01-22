import sys
from threading import Thread
sys.path.append("/home/pi/Anton/Py3Snowboy/snowboy/examples/Python3")
sys.path.append("/home/pi/Anton/PyModules")
import snowboydecoder
import signal
import os
from Anton import Anton

anton = Anton()
interrupted = False

def trigger():
    print("Triggered")
    sys.stdout.flush()

def signal_handler(signal, frame):
    global interrupted
    interrupted = True
    for x in anton.processes:
        x.send_signal(signal)
        x.wait()
    anton.isDead = 1
    anton.isRecording = 1
    os.system("stty sane")

def interrupt_callback():
    global interrupted
    return interrupted

if len(sys.argv) == 1:
    print("Error: need to specify model name")
    print("Usage: python demo.py your.model")
    sys.exit(-1)

model = sys.argv[1:]
sensitivity = [.33, .35]
# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)
detector = snowboydecoder.HotwordDetector(model, sensitivity=sensitivity)
print('Listening... Press Ctrl+C to exit')
# main loop
detector.start(detected_callback=anton.record,
               interrupt_check=interrupt_callback,
               sleep_time=0.03)

detector.terminate()
