/*
 * PC-O-Meter logic and servo control.
 *
 * Developed for the Society of Software Engineers at
 * Rochester Institute of Technology by
 * Corban Mailloux.
 */

// Servo configuration
int servoPin = A4;
int servoMin = 4;
int servoMax = 177;
int wtfAngle = 20; // Angle to increase by for each button press

// Decay configuration
int servoDecayDelay = 2000; // Delay after button press before decay
int servoDecaySpeed = 250; // Decay rate; smaller = faster decay

bool mentoringMode = false;
unsigned long lastPressTime;
Servo servo;
int currentAngle = 0;

int numberOfWedges = 5;
int wedgeBottoms[6];

void setup() {
    // Setup the servo
    servo.attach(servoPin);
    servo.write(servoMin);
    for (int i = 0; i < numberOfWedges; i++)
    {
        wedgeBottoms[i] = ((i / 5.0) * (servoMax - servoMin)) + servoMin;
    }


    // Mentoring mode
    Particle.function("pc-lock", mentoringLock);
    Particle.function("pc-unlock", mentoringUnlock);

    // Expose a function, for POST requests
    Particle.function("pc-trigger", trigger);

    // Subscribe to the buttons
    Particle.subscribe("pc-trigger", triggerSubscribe, MY_DEVICES);
    RGB.control(true);
}

void loop() {
    // Update light color
    if (currentAngle >= wedgeBottoms[4]) {
        RGB.color(255, 0, 0);
    } else if (currentAngle >= wedgeBottoms[3]) {
        RGB.color(255, 128, 0);
    } else if (currentAngle >= wedgeBottoms[2]) {
        RGB.color(255, 255, 0);
    } else if (currentAngle >= wedgeBottoms[1]) {
        RGB.color(0, 255, 0);
    } else {
        RGB.color(0, 0, 255);
    }

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

void updateServo(int angle) {
    if (angle < servoMin) {
        angle = servoMin;
    } else if (angle > servoMax) {
        angle = servoMax;
    }

    currentAngle = angle;
    servo.write(currentAngle);
}

int trigger(String UNUSED) {
    if (mentoringMode)
    {
        return(-1);
    }
    updateServo(currentAngle + wtfAngle);
    lastPressTime = millis();
    return(currentAngle);
}

void triggerSubscribe(const char* UNUSED, const char* UNUSED2) {
    trigger("");
}

// Mentoring mode lock: lock the needle in the current position, or in a given wedge.
int mentoringLock(String zoneString) {
    mentoringMode = true;
    int zone = zoneString.toInt(); // Returns 0 is the conversion fails.
    
    if (zone > 0)
    {
        updateServo(wedgeBottoms[zone - 1] + (0.1 * (servoMax - servoMin)));
    }
}

int mentoringUnlock(String UNUSED) {
    mentoringMode = false;
    updateServo(servoMin);
}