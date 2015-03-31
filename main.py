from time import sleep
import wiringpi2 # For harware PWM for the servo
import RPi.GPIO as GPIO # For general GPIO

# Debug mode
DEBUG_FLAG = True

# Use BCM numbering on the RPi
wiringpi2.wiringPiSetupGpio()
GPIO.setmode(GPIO.BCM)

# Pin numbers
servo_pin = 18

trigger_pin = 22
button1_pin = 23
button2_pin = 24
button3_pin = 25

# Pin configuration
#TODO, change all to pull down, based on the receiver pinout
GPIO.setup(trigger_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button2_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(button3_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Servo configuration, with hardware PWM
wiringpi2.pinMode(servo_pin, wiringpi2.GPIO.PWM_OUTPUT)
wiringpi2.pwmSetMode(wiringpi2.GPIO.PWM_MODE_MS)
wiringpi2.pwmSetClock(384)
wiringpi2.pwmSetRange(1000)

servo_angle_range = (0, 180)
servo_pwm_range = (28, 120)

# Servo decay configuration
servo_decay_delay = 2 # Delay, in seconds, before starting the decay
servo_decay_speed = 0.025 # Rate of decay. Smaller numbers = quicker decay

# Globals
current_angle = 0 # Current servo angle
current_delay = False # Currently delaying for the decay
scaler = None # Scaling function


"""
From http://stackoverflow.com/a/1970037

Creates a scaling function for the servo range.
"""
def make_interpolater(left_min, left_max, right_min, right_max): 
    # Figure out how 'wide' each range is  
    leftSpan = left_max - left_min  
    rightSpan = right_max - right_min  

    # Compute the scale factor between left and right values 
    scaleFactor = float(rightSpan) / float(leftSpan) 

    # create interpolation function using pre-calculated scaleFactor
    def interp_fn(value):
        return right_min + (value-left_min)*scaleFactor

    return interp_fn


"""
Set the servo to the given angle.
"""
def update_servo_angle(angle):
    global current_angle
    global scaler

    # Check if a scaler exists, or make one
    if scaler is None:
        scaler = make_interpolater(
            servo_angle_range[0], servo_angle_range[1], 
            servo_pwm_range[0], servo_pwm_range[1])

    # Ensure the angle is within the servo bounds
    if angle < servo_angle_range[0]:
        angle = servo_angle_range[0]
    elif angle > servo_angle_range[1]:
        angle = servo_angle_range[1]

    # Scale the angle
    pulse = int(scaler(angle))

    debug("Updating to: {0}, pulse: {1}".format(angle, pulse))
    wiringpi2.pwmWrite(servo_pin, pulse)
    current_angle = angle


"""
Called when any button is pressed.
"""
def triggered(channel):

    # Poll the button inputs to see what was pressed.
    #TODO, should each of these have their own interrupt instead?
    button_pressed = None
    if not GPIO.input(button1_pin): #TODO: remove not
        button_pressed = 1
    elif GPIO.input(button2_pin):
        button_pressed = 2
    elif GPIO.input(button3_pin):
        button_pressed = 3
    else:
        debug("Didn't catch that button press, but there was one...")
        #TODO, test/remove this line:
        #update_servo_angle(current_angle + 50)
        return

    debug("Button {0} pressed!".format(button_pressed))
    update_servo_angle(current_angle + 50)
    set_delay()


def set_delay(clear=False):
    global current_delay
    current_delay = not clear

"""
Main entry point.
"""
def main():
    # Start the servo at lowest servo bound
    update_servo_angle(servo_angle_range[0])

    try:
        # Catch the trigger input
        GPIO.add_event_detect(trigger_pin, GPIO.FALLING, callback=triggered, bouncetime=200) #TODO: RISING, because pull down.

        while True:
            if current_delay:
                set_delay(True)
                sleep(servo_decay_delay)
            if current_angle > 0:
                update_servo_angle(current_angle - 1)
                sleep(servo_decay_speed)
    finally:
        # Cleanup
        wiringpi2.pinMode(servo_pin, wiringpi2.GPIO.INPUT)
        GPIO.cleanup()


def debug(string):
    if DEBUG_FLAG:
        print(string)


if __name__ == "__main__":
    main()
