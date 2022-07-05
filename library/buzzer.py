import RPi.GPIO as GPIO  # import the GPIO library
import time  # import the time library
from threading import Thread
from queue import Queue

class Buzzer(Thread):
    def __init__(self, buzzerPin):
        Thread.__init__(self)
        self._gpio = GPIO
        self._gpio.setmode(GPIO.BCM)
        self._gpio.cleanup()
        self._buzzerPin = buzzerPin  # set to GPIO pin 5
        self._gpio.setup(self._buzzerPin, self._gpio.IN)
        self._gpio.setup(self._buzzerPin, self._gpio.OUT)
        self._buzzer = GPIO.PWM(self._buzzerPin,100)
        self._buzzer.ChangeFrequency(300)

        self._commandQ = Queue()

    def __del__(self):
        self._gpio.cleanup()

    def run(self):
        print('START THread')
        while(True):
            while not self._commandQ.empty():
                for tone in self._commandQ.get():
                    if 1 == tone[0]:
                        self.toneOn(tone[1])
                    else:
                        self.toneOff(tone[1])
            time.sleep(0.1)

    def toneOn(self,duration):
        if duration >= 255:
            print('duration ON forever')
            self._buzzer.start(100)
        else:
            print('sound ON for ', duration)
            self._buzzer.start(100)
            time.sleep(duration)
            self._buzzer.stop()

    def toneOff(self,duration):
        if duration >= 255:
            print('duration OFF forever')
            self._buzzer.stop()
        else:
            print('sound OFF for ', duration)
            self._buzzer.stop()
            time.sleep(duration)

    def TONE1(self):
       # notes = [294,330]
        _sequence = [[1,0.3],[0,0.2],[1,0.1],[0,255]]
        print(_sequence)
        self._commandQ.put(_sequence)

    def TONE2(self):
       # notes = [294,330]
        _sequence = [[1,0.1],[0,0.2],[1,0.3],[0,255]]
        print(_sequence)
        self._commandQ.put(_sequence)

    def TONE3(self):
       # notes = [294,330]
        _sequence = [[1,1],[0,0.1],[1,2],[0,255]]
        print(_sequence)
        self._commandQ.put(_sequence)

    def TONE4(self):
       # notes = [294,330]
        _sequence = [[1,2],[0,0.5],[1,2],[0,0.5],[1,2],[0,0.5],[1,2],[0,0.5],[1,2],[0,0.5],[1,2],[0,0.5],[1,2],[0,255]]
        print(_sequence)
        self._commandQ.put(_sequence)

    def TONE_ON(self):
        _sequence = [[1,255]]
        print(_sequence)
        self._commandQ.put(_sequence)

    def TONE_OFF(self):
        _sequence = [[0,255]]
        print(_sequence)
        self._commandQ.put(_sequence)






if __name__ == "__main__":
  #  a = input("Enter Tune number 1-5:")
    buzzer = Buzzer(16)
    buzzer.start()
    buzzer.TONE1()
    time.sleep(1)
    buzzer.TONE2()
    time.sleep(1)
    buzzer.TONE_ON()
    time.sleep(5)
    buzzer.TONE_OFF()
   # buzzer.tone2()
    #buzzer.play(int(a))
    time.sleep(5)
    buzzer.TONE2()