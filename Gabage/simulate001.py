"""
Tester for GPIO GUI interaction using polling
"""

import GPIO as GPIO
import time
import traceback

#GPIO.set_verbosity(3)


def main():
    try:
     #   GPIO.setmode(GPIO.BCM)

      #  GPIO.setwarnings(False)

        GPIO.setup(4, GPIO.OUT)
        GPIO.setup(17, GPIO.OUT)
        GPIO.setup(18, GPIO.OUT)
        GPIO.setup(21, GPIO.OUT)

        GPIO.setup(9, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(11, GPIO.IN)
        GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        while True:
            if GPIO.input(9) == False:
                GPIO.output(4, GPIO.HIGH)
                GPIO.output(17, GPIO.HIGH)

            if GPIO.input(25) == True:
                GPIO.output(4, GPIO.LOW)
                GPIO.output(17, GPIO.LOW)

            if GPIO.input(8) == True:
                GPIO.output(18, GPIO.HIGH)
                GPIO.output(21, GPIO.HIGH)

            if GPIO.input(11) == True:
                GPIO.output(18, GPIO.LOW)
                GPIO.output(21, GPIO.LOW)

        time.sleep(0.01)

#    except Exception:
    #traceback.print_exc()
    finally:
#        GPIO.cleanup()  # this ensures a clean exit
        print('TEST')


main()
