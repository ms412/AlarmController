import RPi.GPIO as GPIO  # import the GPIO library
import time  # import the time library


class Buzzer(object):
    def __init__(self,buzzerPin):
        self._gpio = GPIO
        self._gpio.setmode(GPIO.BCM)
        self._gpio.cleanup()
        self._buzzerPin = buzzerPin  # set to GPIO pin 5
        self._gpio.setup(self._buzzerPin, self._gpio.OUT)
      #  self._buzzer = GPIO.PWM(self.buzzerPin, 1000)  # Set frequency to 1 Khz
        print('oo')
        #buzzer.start(10)

    def __del__(self):
        self._gpio.cleanup()

    def play(self,noteFreq,duration):
        halveWaveTime = 1 / (noteFreq * 2)
        waves = int(duration * noteFreq)
        for i in range(waves):
            self._gpio.output(self._buzzerPin, True)
            time.sleep(halveWaveTime)
            self._gpio.output(self._buzzerPin, False)
            time.sleep(halveWaveTime)

    def tone1(self):
        notes = [294,330]
        duration = [0.1,0.2]
        t = 0

        for n in notes:
            self.play(n,duration[t])
            time.sleep(duration[t] * 0.1)
            t += 1

    def tone2(self):
        notes = [330,294]
        duration = [0.2,0.1]
        t = 0

        for n in notes:
            self.play(n,duration[t])
            time.sleep(duration[t] * 0.1)
            t += 1


    # buzzer.ChangeDutyCycle(10)
    # buzzer.ChangeFrequency(1000)
    # buzzer.stop()



if __name__ == "__main__":
  #  a = input("Enter Tune number 1-5:")
    buzzer = Buzzer(16)
    buzzer.tone1()
   # buzzer.tone2()
    #buzzer.play(int(a))