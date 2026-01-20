# import necessary libraries
from microbit import *
import gc
from machine import time_pulse_us
import neopixel
import music
import radio

# define here your Joy Car Mainboard Revision
joycar_rev = 1.3

# initialize I2C interface for the Joy Car Mainboard
i2c.init(freq=400000, sda=pin20, scl=pin19)

# initialize PWM controller
i2c.write(0x70, b'\x00\x01')
i2c.write(0x70, b'\xE8\xAA')

# the deceleration of a motor bias can be used to compensate for different motor speeds
biasR = 0  # deceleration of the right motor in percent
biasL = 0  # deceleration of the left motor in percent

# control motors using the PWM controller
# PWM0 and PWM1 for the left motor and PWM2 and PWM3 for the right motor
def drive(PWM0, PWM1, PWM2, PWM3):
    # The scale function is used to rescale the bias variables for
    # the calculation of the motor speed
    def scale(num, in_min, in_max, out_min, out_max):
        return (num - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    # Scaling of the deceleration value to the value in percent
    PWM0 = int(PWM0 * (scale(biasR, 0, 100, 100, 0) / 100))
    PWM1 = int(PWM1 * (scale(biasR, 0, 100, 100, 0) / 100))
    PWM2 = int(PWM2 * (scale(biasL, 0, 100, 100, 0) / 100))
    PWM3 = int(PWM3 * (scale(biasL, 0, 100, 100, 0) / 100))

    # transmit value for PWM channel (0-255) to PWM controller
    # 0x70 is the I2C address of the controller.
    # the byte with the PWM value is added to the byte for the channel
    i2c.write(0x70, b'\x02' + bytes([PWM0]))
    i2c.write(0x70, b'\x03' + bytes([PWM1]))
    i2c.write(0x70, b'\x04' + bytes([PWM2]))
    i2c.write(0x70, b'\x05' + bytes([PWM3]))

# get all sensor data
def fetchSensorData():
    # Since the zfill function is not included in micro:bit Micropython,
    # it must be inserted as a function
    def zfill(s, width):
        return '{:0>{w}}'.format(s, w=width)

    # Read hexadecimal data and convert to binary
    data = "{0:b}".format(ord(i2c.read(0x38, 1)))
    # fill in the data to 8 digits if necessary
    data = zfill(data, 8)
    # declare bol_data_dict as dictionary
    bol_data_dict = {}
    # Counter for the loop that enters the data from data into bol_data_dict
    bit_count = 7
    # Transfer the data from data to bol_data_dict
    for i in data:
        if i == "0":
            bol_data_dict[bit_count] = False
            bit_count -= 1
        else:
            bol_data_dict[bit_count] = True
            bit_count -= 1

    # after main board revision 1.3, the speed sensors are on separate pins
    if joycar_rev >= 1.3:
        bol_data_dict[8], bol_data_dict[9] = bol_data_dict[0], bol_data_dict[1]
        bol_data_dict[0] = bool(pin14.read_digital())
        bol_data_dict[1] = bool(pin15.read_digital())

    # bit 0 = SpeedLeft, bit 1 = SpeedRight, bit 2 = LineTrackerLeft,
    # bit 3 = LineTrackerMiddle, bit 4 = LineTrackerRight,
    # bit 5 = ObstclLeft, bit 6 = ObstclRight, bit 7 = free pin(7)
    # (bit 8 = free (pin0) bit 9 = free (pin1)) - just with revision 1.3 or newer
    return bol_data_dict

# define pins for ultrasonic sensor
trigger = pin8
echo = pin12

# initialize pins for ultrasonic sensor
trigger.write_digital(0)
echo.read_digital()

# method to calculate distance from ultrasonic sensor
def get_distance():
    # collect garbage
    gc.collect()
    # set short impulse onto the trigger pin
    trigger.write_digital(1)
    trigger.write_digital(0)
    # meassure time until echo pin is high
    duration = time_pulse_us(echo, 1)
    # calculate distance
    distance = ((duration / 1000000) * 34300) / 2
    # return the distance rounded to 2 decimal digits
    return round(distance, 2)

# setup pins for servomotor
pin1.set_analog_period(10)
pin13.set_analog_period(10)

# method to change position to servo motors
def servo(channel, position):
    # method to scale from 0-180 (°) to 100-200 (us)
    def scale(num, in_min, in_max, out_min, out_max):
        # Rückgabe des auf eine ganze Zahl gerundeten Werts
        return (round((num - in_min) * (out_max - out_min) /
                (in_max - in_min) + out_min))
    # check if position is in range
    if position < 0 and position > 180:
        return "position not in range"
    # send position to selected channel
    if channel == 1:
        pin1.write_analog(scale(position, 0, 180, 100, 200))
    elif channel == 2:
        pin13.write_analog(scale(position, 0, 180, 100, 200))


# define object for the lights
np = neopixel.NeoPixel(pin0, 8)

# define values for the lights
# which LEDs to activate
headlights = (0, 3)
backlights = (5, 6)
indicator_left = (1, 4)
indicator_right = (2, 7)
indicator_warning = (1, 2, 4, 7)

# which colour to show on LEDs
led_white = (60, 60, 60)
led_red = (60, 0, 0)
led_off = (0, 0, 0)
led_red_br = (255, 0, 0)
led_orange = (100, 35, 0)

# method to activate/deactivate lights
def lights(on=True):
    if on:
        for x, y in zip(headlights, backlights):
            # define white for the headlights
            np[x] = led_white
            # define dark red for the backlights
            np[y] = led_red
    else:
        for x, y in zip(headlights, backlights):
            # define black for the headlights and backlights
            np[x] = led_off
            np[y] = led_off
    np.show()

# activate/deactivate the light for driving backwards
def lightsBack(on=True):
    if on:
        # set left backlight to white
        np[backlights[0]] = led_white
        np.show()
    else:
        # set left backlight to black
        np[backlights[0]] = led_off
        np.show()

# method to activate/deactivate the indicators
# variable for the method to compare when the lights were last active
last_ind_act = running_time()
def lightsIndicator(direction, on=True):
    # to be able to change the global variable
    global last_ind_act
    # activate garbage collector
    gc.collect()

    # if you want to switch off indicators
    if on is False:
        # deactivate LEDs
        for x in direction:
            np[x] = led_off
        np.show()
        # close the method
        return

    # activate/deactivate indicators after 400 ms
    if running_time() - last_ind_act >= 400:
        # activate LEDs if LEDs are off
        if np[direction[0]] == led_off:
            for x in direction:
                np[x] = led_orange
        # deactivate LEDs if LEDs are on
        else:
            for x in direction:
                np[x] = led_off
        np.show()
        # set global variable to current running time
        last_ind_act = running_time()

# activate radio
radio.on()

# variable to determine in which mode we are
# 0 - Obstacle detection, 1 - Line tracking, 2 - remote control
mode = 0

while True:
    # if button a pressed increase mode by 1
    if button_a.is_pressed() == 1:
        mode += 1
        if mode > 2:
            mode = 0
        sleep(500)
    # if button b pressed decrease mode by 1
    if button_b.is_pressed() == 1:
        mode -= 1
        if mode < 0:
            mode = 2
        sleep(500)
    # show mode on microbit
    display.show(mode)

    # Obstacle detection
    if mode == 0:
        # activate lights
        lights()
        lightsIndicator(indicator_warning, on=False)
        # get data from IO expander
        sensor_data = fetchSensorData()
        # check if both sensors detect an obstacle
        if sensor_data[5] is False and sensor_data[6] is False:
            # evade obstacle
            drive(255, 40, 40, 255)
            sleep(500)
        # check if obstacle is detected on the left
        elif sensor_data[5] is False and sensor_data[6] is True:
            # evade obstacle
            drive(255, 40, 0, 0)
            sleep(500)
        # check if obstacle is detected on the right
        elif sensor_data[6] is False and sensor_data[5] is True:
            # evade obstacle
            drive(0, 0, 255, 40)
            sleep(500)
        else:
            # drive forwards
            drive(40, 255, 40, 255)
        # check if there is more than 20cm otherwise do this rotine
        if get_distance() < 20:
            # stop the JoyCar
            drive(0, 0, 0, 0)
            sleep(500)
            # set servomotor to the far right an dmeasure distance
            servo(1, 0)
            sleep(500)
            distance_right = get_distance()
            # set servomotor to the far left an dmeasure distance
            servo(1, 180)
            sleep(500)
            distance_left = get_distance()
            # set servomotor back in the middle
            servo(1, 90)
            sleep(500)
            # if on the left side is less space than on the right
            if distance_left < distance_right:
                # turn right
                drive(255, 0, 0, 255)
                sleep(500)
            # if on the right side is less space than on the left
            else:
                # turn left
                drive(0, 255, 255, 0)
                sleep(500)

    # Line tracking
    elif mode == 1:
        # activate lights
        lights()
        lightsIndicator(indicator_warning, on=False)
        # get data from IO expander
        sensor_data = fetchSensorData()
        # check if only the left sensor detects a line
        if sensor_data[2] is True and sensor_data[3] is False and sensor_data[4] is False:
            # correct JoyCar back to the line
            drive(60, 150, 0, 0)
        # check if only the middle sensor detects a line
        elif sensor_data[2] is False and sensor_data[3] is True and sensor_data[4] is False:
            # drive forwards
            drive(30, 150, 30, 150)
        # check if only the right sensor detects a line
        elif sensor_data[2] is False and sensor_data[3] is False and sensor_data[4] is True:
            # correct JoyCar back to the line
            drive(0, 0, 60, 150)
        # check if stop symbol is recognized
        elif sensor_data[2] is True and sensor_data[3] is False and sensor_data[4] is True:
            # stop the JoyCar
            drive(0, 0, 0, 0)
        else:
            # drive forwards
            drive(30, 150, 30, 150)

    # Remote control
    elif mode == 2:
        # receive some sent data
        incoming = radio.receive()

        # if data was received
        if incoming is not None:
            try:
                # 0 - direction, 1 - speed, 2 - lights & horn
                speed = int(incoming[1])
            except ValueError:
                speed = 0

            # drive in received direction with received speed
            if incoming[0] == "l":
                drive(speed * 4.44, speed * 28.33, 0, 0)
            elif incoming[0] == "r":
                drive(0, 0, speed * 4.44, speed * 28.33)
            elif incoming[0] == "f":
                drive(speed * 4.44, speed * 28.33, speed * 4.44, speed * 28.33)
            elif incoming[0] == "b":
                drive(speed * 28.33, speed * 4.44, speed * 28.33, speed * 4.44)
            else:
                drive(0, 0, 0, 0)

            # when driving backwards turn on backlights
            if incoming[0] == "b":
                lightsBack()
            else:
                lightsBack(on=False)

            # special functions
            if incoming[2] == "a":
                # use the horn
                music.pitch(440, 100, pin=pin16)
            elif incoming[2] == "b":
                # activate the light
                lights()
            elif incoming[2] == "c":
                # activate hazard lights
                lightsIndicator(indicator_warning)
            else:
                # deactivate lights
                lights(on=False)
                lightsIndicator(indicator_warning, on=False)
        else:
            # stop JoyCar when nothing is received
            drive(0, 0, 0, 0)
            # activate hazard lights
            lightsIndicator(indicator_warning)
