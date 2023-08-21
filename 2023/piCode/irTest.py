import time # needed for sleep
import RPi.GPIO as GPIO # needed for pin access

GPIO.setmode(GPIO.BCM)
GPIO.setup(14, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

while True:

	time.sleep(1)

	if GPIO.input(14):
		print('H')
	else:
		print('L')

GPIO.cleanup() # cleanup all GPIO
