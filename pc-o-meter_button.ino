/*
 * PC-O-Meter buttons.
 *
 * Developed for the Society of Software Engineers at
 * Rochester Institute of Technology by
 * Corban Mailloux.
 */

// Unique value for each of the buttons.
const int buttonNumber = 1;

const int buttonPin = D1;

void setup() {
    pinMode(buttonPin, INPUT_PULLUP);
    RGB.control(true);
}

void loop() {
    // Update light color
    RGB.color(0, 255, 0);

    // TODO: Switch to an interrupt?
    if (digitalRead(buttonPin) == LOW) {
        Particle.publish("pc-trigger", String(buttonNumber), PRIVATE);
        RGB.color(255, 0, 0);

        // Avoid multiple triggers
        while (digitalRead(buttonPin) == LOW) {
            // Do nothing
            delay(100);
        }

        // Debounce
        delay(100);
    }
}
