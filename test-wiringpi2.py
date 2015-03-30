from time import sleep
import wiringpi2

wiringpi2.wiringPiSetupGpio()

# Pin numbers
servo_pin = 18

# Servo configuration
wiringpi2.pinMode(servo_pin, 2)
wiringpi2.pwmSetMode(0)
wiringpi2.pwmSetClock(384)
wiringpi2.pwmSetRange(1000)


servo_angle_range = (0, 180)
servo_pwm_range = (28, 120)

# Global current angle
current_angle = 0

scaler = None


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
    if angle < 0:
        angle = 0
    elif angle > 180:
        angle = 180

    pulse = int(scaler(angle))

    print("Updating to: {0}, pulse: {1}".format(angle, pulse))
    wiringpi2.pwmWrite(servo_pin, pulse)
    current_angle = angle

for i in range(1, 181):
	update_servo_angle(i)
	sleep(0.025)

for i in range(180, 0, -1):
	update_servo_angle(i)
	sleep(0.025)

update_servo_angle(90)
