import RPi.GPIO as GPIO
import time


class WaterSensorLog:
    def __init__(self, file_name='./level.txt', limit=100):
        self.file_name = file_name
        self.limit = limit

    def push(self, distance):
        with open(self.file_name, 'r') as file:
            records = file.readlines()

        if len(records) >= self.limit:
            records.pop(0)
        
        record = '{datetime},{distance}\n'.format(datetime=int(time.time()), distance=distance)
        records.append(record)

        with open(self.file_name, 'w') as file:
            file.write(''.join(records))


try:
    GPIO.setmode(GPIO.BOARD)

    PIN_TRIGGER = 7
    PIN_ECHO = 11

    GPIO.setup(PIN_TRIGGER, GPIO.OUT)
    GPIO.setup(PIN_ECHO, GPIO.IN)

    GPIO.output(PIN_TRIGGER, GPIO.LOW)

    print ("Waiting for sensor to settle")

    time.sleep(2)

    print ("Calculating distance")

    GPIO.output(PIN_TRIGGER, GPIO.HIGH)

    time.sleep(0.00001)

    GPIO.output(PIN_TRIGGER, GPIO.LOW)

    while GPIO.input(PIN_ECHO) == 0:
        pulse_start_time = time.time()
    while GPIO.input(PIN_ECHO) == 1:
        pulse_end_time = time.time()

    pulse_duration = pulse_end_time - pulse_start_time
    distance = round(pulse_duration * 17150, 2)

    # write distance to file
    log = WaterSensorLog('./level.txt')
    log.push(distance)

    print ('Distance {distance} cm'.format(distance=distance))

finally:
    GPIO.cleanup()
