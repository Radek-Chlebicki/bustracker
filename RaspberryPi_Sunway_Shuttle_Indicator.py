import urllib.request
import time
import timeit
import math
import RPi.GPIO as gpio

# timer  = -10
# bus1timeatchange
# bus1timesincelast change

busflag = 1

# these are used to calculate the rate of blinking
bus1stopprevious = 0
b1tac = 0
b1tslc = 0
bus2stopprevious = 0
b2tac = 0
b2tslc = 0
LOGBASE = 1.5
ROOFBLINK = 0.5
BLINKPWMDC = 50

# the rates of blinking
blinkratebus1 = 1
blinkratebus2 = 1

# servo control variables
SERVOFREQUENCY = 50
servodutycycle = 5

# PIN NUMBErs
# bus1blink rate led
B1BRLED = 11
B2BRLED = 13
# bus1controlLED
B1CLED = 18
B2CLED = 22
# servo control led
SERVOCONTROLLED = 16
# servopin
SERVOPIN = 12
# button
BUTTON = 36

GROUND = 6
L3V3 = 1

# declare what the pins do and set up pwming pins

# use numbering scheme of physical pins
gpio.setmode(gpio.BOARD)

# pwmled duty cycle is 50 % and frequency is 1 but will be changed
gpio.setup(B1BRLED, gpio.OUT)
gpio.setup(B2BRLED, gpio.OUT)
b1brledpwm = gpio.PWM(B1BRLED, blinkratebus1)  # pin, frequency
b1brledpwm.start(BLINKPWMDC)
# b1brledpwm.ChangeDutyCycle(BLINKPWMDC)# argument is a percentage
b2brledpwm = gpio.PWM(B2BRLED, blinkratebus2)
b2brledpwm.start(BLINKPWMDC)
# b2brledpwm.ChangeDutyCycle(BLINKPWMDC)

# these LEDs will be set to high and low only
gpio.setup(B1CLED, gpio.OUT)
gpio.output(B1CLED, 1)

gpio.setup(B2CLED, gpio.OUT)
gpio.output(B2CLED, 1)

# servo led is also only on or off
gpio.setup(SERVOCONTROLLED, gpio.OUT)
gpio.output(SERVOCONTROLLED, 0)

# pwm for servo
gpio.setup(SERVOPIN, gpio.OUT)
servopwm = gpio.PWM(SERVOPIN, SERVOFREQUENCY)
servopwm.start(servodutycycle)

# button to choose bus
gpio.setup(BUTTON, gpio.IN)


def stops():
    busposition = urllib.request.urlopen("http://trace.my/sunwayshuttle/showbus/showLoc-0701.php")
    buspositionstring = str(busposition.read())
    parselist = buspositionstring.split(",")
    bus1stoppre = parselist[3]
    bus2stoppre = parselist[9]

    def stringprocess(astring):
        templist = astring.split(":")
        prefinal = templist[1]
        final = prefinal.replace('"', '')
        return final

    bus1stop = stringprocess(bus1stoppre)
    bus2stop = stringprocess(bus2stoppre)
    return bus1stop, bus2stop


def shakeneedle():
    servopwm.ChangeDutyCycle(6)
    time.sleep(0.5)
    for i in range(0, 5):
        servopwm.ChangeDutyCycle(8)
        time.sleep(0.5)
        servopwm.ChangeDutyCycle(6)
        time.sleep(0.5)
    servopwm.ChangeDutyCycle(5)


def setservocontrolled(stopnumber):
    if stopnumber > 6:
        gpio.output(SERVOCONTROLLED, 1)
    else:
        gpio.output(SERVOCONTROLLED, 0)


def setservoneedle(stopnumber):
    setservocontrolled(stopnumber)

    if stopnumber == 1 or stopnumber == 7:
        servopwm.ChangeDutyCycle(10.4)
    if stopnumber == 2 or stopnumber == 8:
        servopwm.ChangeDutyCycle(9.3)
    if stopnumber == 3 or stopnumber == 9:
        servopwm.ChangeDutyCycle(7.8)
    if stopnumber == 4 or stopnumber == 10:
        servopwm.ChangeDutyCycle(6.3)
    if stopnumber == 5 or stopnumber == 11:
        servopwm.ChangeDutyCycle(4.7)
    if stopnumber == 6:
        servopwm.ChangeDutyCycle(3.3)


starttime = time.time()

try:
    while True:

        print("First in loop")

        bus1stop, bus2stop = stops()
        if bus1stop.isdigit():
            bus1stop = int(bus1stop)
        if bus2stop.isdigit():
            bus2stop = int(bus2stop)
        print("")
        print("bus1stop: " + str(bus1stop) + " bus2stop: " + str(bus2stop))
        print("")

        # 1 ) determine and change blink rates

        # if bus stop is not same as previous change it and record b1tac
        # use b1 tac to calculate time since last change
        # use time since last change to calculate the blink rate
        # ensure that blink rate does not exceed the maximum ROOFBLINK

        if type(bus1stop) == int and bus1stop > 0 and bus1stop < 12:
            if bus1stopprevious != bus1stop:
                bus1stopprevious = bus1stop
                b1tac = time.time() - starttime

            b1tslc = (time.time() - starttime - b1tac) / 60
            blinkratebus1 = -2 * b1tslc + 20
            print("blink rate before roof blink bus 1: "+str(blinkratebus1) +"   b1tslc: " + str(b1tslc) +"  b1tac: " + str(b1tac))
            print("")
            if blinkratebus1 < ROOFBLINK:
                blinkratebus1 = ROOFBLINK

        else:
            print("else case bus 1")
            print("")
            blinkratebus1 = 0.1

        print("bus1rate: "+ str(blinkratebus1))
        print("")
        b1brledpwm.ChangeFrequency(blinkratebus1)

        # bus 2
        if type(bus2stop) == int and bus2stop > 0 and bus2stop < 12:
            if bus2stopprevious != bus2stop:
                bus2stopprevious = bus2stop
                b2tac = time.time() -starttime

            b2tslc = (time.time() -starttime -b2tac) / 60
            blinkratebus2 = -2 * b2tslc + 20
            print("blink rate before roof blink bus 2: "+str(blinkratebus2)+ "   b2tslc: " + str(b2tslc)+"  b2tac: " + str(b2tac))
            print("")

            if blinkratebus2 < ROOFBLINK:
                blinkratebus2 = ROOFBLINK

        else:
            print("else case bus 2")
            print("")
            blinkratebus2 = 0.1

        print("bus2rate: "+ str(blinkratebus2))
        print("")
        b2brledpwm.ChangeFrequency(blinkratebus2)

        # 1.5 check for servo control switch

        # switch is open
        if gpio.input(BUTTON) == 1:
            busflag = 1

        # switch is closed
        elif gpio.input(BUTTON) == 0:
            busflag = 2

        # 1.6 set bus control led

        if busflag == 1:
            print("changed to bus 1")
            print("")
            gpio.output(B1CLED, 1)
            gpio.output(B2CLED, 0)

        if busflag == 2:
            print("changedtobus 2")
            print("")
            gpio.output(B1CLED, 0)
            gpio.output(B2CLED, 1)

        # 3 set servo and its led

        if busflag == 1:
            if type(bus1stop) != int or bus1stop < 1 or bus1stop > 11:
                print("Bus 1 shake needle: ")
                print("")
                shakeneedle()
            else:
                # set servo led function
                # set needle function
                print("bus 1 point needle")
                print("")
                setservoneedle(bus1stop)

        if busflag == 2:
            if type(bus2stop) != int or bus2stop < 1 or bus2stop > 11:
                print("bus 2 shake needle: ")
                print("")
                shakeneedle()
            else:
                # set servo led function
                # set needle function
                print("bus 1 point needle")
                print("")
                setservoneedle(bus2stop)

        print(" last in loop")
        time.sleep(10)

except KeyboardInterrupt:
    pass

print("finish of program")
gpio.cleanup()
