/*
 * PC-O-Meter logic and servo control.
 *
 * Developed for the Society of Software Engineers at
 * Rochester Institute of Technology by
 * Corban Mailloux.
 */

// Servo configuration
const int servoPin = A4;
const int servoMin = 4; // Minimum angle (ideally 0)
const int servoMax = 177; // Maximum angle (ideally 180)
const int wtfAngle = 20; // Angle to increase by for each button press

// Decay configuration
const int servoDecayDelay = 2000; // Delay after button press before decay
const int servoDecaySpeed = 250; // Decay rate; smaller = faster decay

// Layout configuration
const int numberOfWedges = 5;


// Globals
int wedgeBottoms[numberOfWedges]; // Calculated degrees of the wedges
bool mentoringMode = false;
unsigned long lastPressTime; // millis() when the last trigger happened
Servo servo;
int currentAngle = 0;

void setup() {
    // Setup the servo
    servo.attach(servoPin);
    servo.write(servoMin);

    // Calculate the bottoms of the wedges
    for (int i = 0; i < numberOfWedges; i++)
    {
        wedgeBottoms[i] = ((i / (float)numberOfWedges) * (servoMax - servoMin)) + servoMin;
    }

    // Expose POST functions for mentoring mode
    Particle.function("pc-lock", mentoringLock);
    Particle.function("pc-unlock", mentoringUnlock);

    // Expose POST function for triggers
    Particle.function("pc-trigger", trigger);

    // Subscribe to the buttons for triggers
    Particle.subscribe("pc-trigger", triggerSubscribe, MY_DEVICES);
    
    RGB.control(true); // Take over the on-board RGB LED
}

void loop() {
    // Update light color
    if (currentAngle >= wedgeBottoms[4]) {
        RGB.color(255, 0, 0); // Red
    } else if (currentAngle >= wedgeBottoms[3]) {
        RGB.color(255, 128, 0); // Orange
    } else if (currentAngle >= wedgeBottoms[2]) {
        RGB.color(255, 255, 0); // Yellow
    } else if (currentAngle >= wedgeBottoms[1]) {
        RGB.color(0, 255, 0); // Green
    } else {
        RGB.color(0, 0, 255); // Blue
    }

    // Don't update the meter in mentoring mode.
    if (mentoringMode){
        delay(500);
    }
    else
    {
        if ((millis() - lastPressTime) >= servoDecayDelay) {
            if (currentAngle > servoMin) {
                updateServo(currentAngle - 1);
                delay(servoDecaySpeed);
            }
        }
    }
}

// Set the servo to the given angle and update currentAngle
void updateServo(int angle) {
    if (angle < servoMin) {
        angle = servoMin;
    } else if (angle > servoMax) {
        angle = servoMax;
    }

    currentAngle = angle;
    servo.write(currentAngle);
}

// Bump up the angle by one WTF
int trigger(String UNUSED) {
	// Block inputs in mentoring mode
    if (mentoringMode)
    {
        return(-1);
    }

    updateServo(currentAngle + wtfAngle);
    lastPressTime = millis();
    return(currentAngle);
}

// Pass-through for the subscribe trigger
void triggerSubscribe(const char* UNUSED, const char* UNUSED2) {
    trigger("");
}

// Mentoring mode lock: lock the needle in the current position, or in a given wedge.
int mentoringLock(String zoneString) {
    mentoringMode = true;
    int zone = zoneString.toInt(); // Returns 0 is the conversion fails.
    
    // Inform the buttons that mentoring mode is on.
    Particle.publish("pc-b-lock-y", String(zone), PRIVATE);
    
    if ((zone > 0) && (zone <= numberOfWedges))
    {
        updateServo(wedgeBottoms[zone - 1] + ((1.0 / (2 * numberOfWedges)) * (servoMax - servoMin)));
    }
}

// Mentoring unlock: restore normal functionality
int mentoringUnlock(String UNUSED) {
    mentoringMode = false;

    // Inform the buttons that mentoring mode is off.
    Particle.publish("pc-b-lock-n", "", PRIVATE);

    updateServo(servoMin);
}