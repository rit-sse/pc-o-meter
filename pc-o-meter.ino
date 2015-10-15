/*
 * PC-O-Meter logic and servo control.
 *
 * Developed for the Society of Software Engineers at
 * Rochester Institute of Technology by
 * Corban Mailloux.
 *
 * October 14, 2015
 */

// Servo configuration
int servoPin = A4;
int servoMin = 0;
int servoMax = 160;
int wtfAngle = 20; // Angle to increase by for each button press

// Decay configuration
int servoDecayDelay = 2000; // Delay after button press before decay
int servoDecaySpeed = 250; // Decay rate; smaller = faster decay


unsigned long lastPressTime;
Servo servo;
int currentAngle = 0;

void setup() {
    servo.attach(servoPin);

    // Expose a function, for POST requests
    Particle.function("SSE_PC-O-Meter_Trigger", trigger);

    // Subscribe to the buttons
    Particle.subscribe("SSE_PC-O-Meter_Trigger", triggerSubscribe, MY_DEVICES);
    RGB.control(true);
}

void loop() {
    // Update light color
    if (currentAngle >= (0.8 * servoMax)) {
        RGB.color(255, 0, 0);
    } else if (currentAngle >= (0.6 * servoMax)) {
        RGB.color(255, 128, 0);
    } else if (currentAngle >= (0.4 * servoMax)) {
        RGB.color(255, 255, 0);
    } else if (currentAngle >= (0.2 * servoMax)) {
        RGB.color(0, 255, 0);
    } else {
        RGB.color(0, 0, 255);
    }

    if ((millis() - lastPressTime) >= servoDecayDelay) {
        if (currentAngle > servoMin) {
            updateServo(currentAngle - 1);
            delay(servoDecaySpeed);
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
    updateServo(currentAngle + wtfAngle);
    lastPressTime = millis();
    return(currentAngle);
}

void triggerSubscribe(const char* UNUSED, const char* UNUSED2) {
    trigger("");
}
