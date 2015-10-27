#!/usr/bin/env python3

import wiringpi2 # For harware PWM for the servo

# Debug mode
DEBUG_FLAG = True

# Use BCM numbering on the RPi
wiringpi2.wiringPiSetupGpio()

# Pin numbers
servo_pin = 18

# Servo configuration, with hardware PWM
wiringpi2.pinMode(servo_pin, wiringpi2.GPIO.PWM_OUTPUT)
wiringpi2.pwmSetMode(wiringpi2.GPIO.PWM_MODE_MS)
wiringpi2.pwmSetClock(384)
wiringpi2.pwmSetRange(1000)

servo_angle_range = (0, 180) # Range of motion for the servo
servo_pwm_range = (30, 118) # PWM range for the servo

# Globals
current_angle = 0 # Current servo angle
current_delay = False # Currently delaying for the decay
scaler = None # Scaling function


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


def main():
    """Main entry point."""
    print("Angle testing active...")
    # Start the servo at lowest servo bound
    update_servo_angle(servo_angle_range[0])

    try:
        while True:
            new_angle = 0
            new_angle = int(input("Angle: "))
            update_servo_angle(new_angle)
    except KeyboardInterrupt:
        pass
    finally:
        print("Exiting...")
        # Cleanup
        wiringpi2.pinMode(servo_pin, wiringpi2.GPIO.INPUT)


def debug(string):
    """Print the string, if debug mode is active."""
    if DEBUG_FLAG:
        print(string)

if __name__ == "__main__":
    main()
