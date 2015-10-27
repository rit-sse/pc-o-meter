#!/usr/bin/env python3

from time import sleep
import wiringpi2 # For harware PWM for the servo
import RPi.GPIO as GPIO # For general GPIO

# Debug mode
DEBUG_FLAG = False

# Use BCM numbering on the RPi
wiringpi2.wiringPiSetupGpio()
GPIO.setmode(GPIO.BCM)

# Pin numbers
servo_pin = 18

trigger_pin = 22
button1_pin = 23
button2_pin = 24
button3_pin = 25
mentors_pin = 8

# Pin configuration
GPIO.setup(
    (trigger_pin, button1_pin, button2_pin, button3_pin, mentors_pin),
    GPIO.IN, 
    pull_up_down=GPIO.PUD_DOWN)

# Servo configuration, with hardware PWM
wiringpi2.pinMode(servo_pin, wiringpi2.GPIO.PWM_OUTPUT)
wiringpi2.pwmSetMode(wiringpi2.GPIO.PWM_MODE_MS)
wiringpi2.pwmSetClock(384)
wiringpi2.pwmSetRange(1000)

servo_angle_range = (0, 180) # Range of motion for the servo
servo_pwm_range = (30, 118) # PWM range for the servo

wtf_angle = 18 # Amount to increase by for each button press

mentor_mode_angles = (0, 13, 51, 87, 127, 162, 180) # Fixed angles for mentor mode

# Servo decay configuration
servo_decay_delay = 2 # Delay, in seconds, before starting the decay
servo_decay_speed = 0.5 # Rate of decay. Smaller numbers = quicker decay

# Globals
current_angle = 0 # Current servo angle
current_delay = False # Currently delaying for the decay
scaler = None # Scaling function
mentor_mode = 0 # Mentor mode


def make_interpolater(left_min, left_max, right_min, right_max):
    """Scaling function for the servo range.

    From http://stackoverflow.com/a/1970037
    """
    # Figure out how 'wide' each range is  
    leftSpan = left_max - left_min  
    rightSpan = right_max - right_min  

    # Compute the scale factor between left and right values 
    scaleFactor = float(rightSpan) / float(leftSpan) 

    # create interpolation function using pre-calculated scaleFactor
    def interp_fn(value):
        return right_min + (value-left_min)*scaleFactor

    return interp_fn


def update_servo_angle(angle):
    """Set the servo to the given angle."""
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


def triggered(channel):
    """Called when any button is pressed."""
    # Poll the button inputs to see what was pressed.
    #TODO, should each of these have their own interrupt instead?
    button_pressed = None
    if GPIO.input(mentors_pin):
        debug("Mentor button pressed!")
        mentor_button()
        return
    elif GPIO.input(button1_pin):
        button_pressed = 1
    elif GPIO.input(button2_pin):
        button_pressed = 2
    elif GPIO.input(button3_pin):
        button_pressed = 3
    else:
        debug("Triggered, but didn't catch which button was pressed...")
        return

    if mentor_mode == 0 and button_pressed is not None:
        debug("Button {0} pressed!".format(button_pressed))
        update_servo_angle(current_angle + wtf_angle)
        set_delay()


def set_delay():
    """Enable the decay delay."""
    global current_delay
    current_delay = True


def clear_delay():
    """Disable the decay delay."""
    global current_delay
    current_delay = False


def mentor_button():
    """Called when the mentor button is pressed.

    Each press locks the meter at a given point in the mentor_mode_angles tuple.
    The final press resets the meter to normal mode.
    """
    global mentor_mode

    mentor_mode += 1

    if mentor_mode > len(mentor_mode_angles):
        debug("Exit mentor mode")
        # Sweep the servo to signal exiting of mentor mode
        update_servo_angle(servo_angle_range[0])
        sleep(0.1)
        for i in range(servo_angle_range[0], servo_angle_range[1], 2):
            update_servo_angle(i)
            sleep(0.005)
        for i in range(servo_angle_range[1], servo_angle_range[0], -2):
            update_servo_angle(i)
            sleep(0.005)
        update_servo_angle(servo_angle_range[0])
        mentor_mode = 0
    else:
        update_servo_angle(mentor_mode_angles[mentor_mode - 1])


def main():
    """Main entry point."""
    print("PC-O-Meter active...")
    # Start the servo at lowest servo bound
    update_servo_angle(servo_angle_range[0])

    try:
        # Catch the trigger input
        GPIO.add_event_detect(trigger_pin, GPIO.RISING, callback=triggered, bouncetime=400)

        while True:
            if mentor_mode != 0:
                sleep(0.5) # Just to avoid complete "do-nothing" loop
                continue
            if current_delay:
                clear_delay()
                sleep(servo_decay_delay)
            if current_angle > 0:
                update_servo_angle(current_angle - 1)
                sleep(servo_decay_speed)
    except KeyboardInterrupt:
        pass
    finally:
        print("PC-O-Meter exiting...")
        # Cleanup
        wiringpi2.pinMode(servo_pin, wiringpi2.GPIO.INPUT)
        GPIO.cleanup()


def debug(string):
    """Print the string, if debug mode is active."""
    if DEBUG_FLAG:
        print(string)

if __name__ == "__main__":
    main()
