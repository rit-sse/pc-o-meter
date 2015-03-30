import RPIO
from RPIO import PWM
from time import sleep

# Debug mode
DEBUG_FLAG = True

# Use BCM numbering on the RPi
RPIO.setmode(RPIO.BCM)

# Pin numbers
servo_pin = 18

trigger_pin = 22
button1_pin = 23
button2_pin = 24
button3_pin = 25

# Pin configuration
#TODO, change to pull down, based on the receiver pinout
RPIO.setup(trigger_pin, RPIO.IN, pull_up_down=RPIO.PUD_UP)
RPIO.setup(button1_pin, RPIO.IN, pull_up_down=RPIO.PUD_DOWN)
RPIO.setup(button2_pin, RPIO.IN, pull_up_down=RPIO.PUD_DOWN)
RPIO.setup(button3_pin, RPIO.IN, pull_up_down=RPIO.PUD_DOWN)

# Servo configuration
servo_angle_range = (0, 180)
servo_microsec_range = (550, 2400)
RPIO.setup(servo_pin, RPIO.OUT)
servo = PWM.Servo(pulse_incr_us=1)

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
            servo_microsec_range[0], servo_microsec_range[1])

    # Ensure the angle is within the servo bounds
    if angle < 0:
        angle = 0
    elif angle > 180:
        angle = 180

    microsec = int(scaler(angle))

    debug("Updating to: {0}, micro: {1}".format(angle, microsec))
    servo.set_servo(servo_pin, microsec)
    current_angle = angle


"""
Called when any button is pressed.
"""
def triggered(gpio_id, value):

    # Poll the button inputs to see what was pressed.
    #TODO, should each of these have their own interrupt instead?
    button_pressed = None
    if RPIO.input(button1_pin):
        button_pressed = 1
    elif RPIO.input(button2_pin):
        button_pressed = 2
    elif RPIO.input(button3_pin):
        button_pressed = 3
    else:
        debug("Didn't catch that button press, but there was one...")
        #TODO, test/remove this line:
        update_servo_angle(current_angle + 50)
        return

    debug("Button {0} pressed!".format(button_pressed))
    update_servo_angle(current_angle + 50)


"""
Main entry point.
"""
def main():
    # Start the servo at 0
    update_servo_angle(0)

    try:
        # Catch the trigger input
        #TODO, change to pull down, based on the receiver pinout
        RPIO.add_interrupt_callback(trigger_pin, triggered, edge="rising", pull_up_down=RPIO.PUD_UP, debounce_timeout_ms=50)

        RPIO.wait_for_interrupts(threaded=True)

        while True:
            if current_angle > 0:
                update_servo_angle(current_angle - 10)
                sleep(1)

    except:
        raise
    finally:
        RPIO.cleanup()

def debug(string):
    if DEBUG_FLAG:
        print(string)


if __name__ == "__main__":
    main()
