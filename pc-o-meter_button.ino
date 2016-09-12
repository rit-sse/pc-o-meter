/*
 * PC-O-Meter buttons.
 *
 * Developed for the Society of Software Engineers at
 * Rochester Institute of Technology by
 * Corban Mailloux.
 */

// Configuration
const int buttonNumber = 1; // Unique value for each of the buttons.
const int buttonPin = D1;
const int blinkRate = 2000; // Milliseconds between blinks in mentoring mode


// Globals
bool mentoringMode = false;
int mentoringZone = 0;
unsigned long blinkTime; // millis() since the last blink
bool blinkOn = false;

// Globals for button debouncing
int buttonCounter = 0; // how many times we have seen new value
int buttonReading; // the current value read from the input pin
int currentButtonState = LOW; // the debounced input value
long lastButtonSampleTime = 0; // the last time the output pin was sampled
int debounceCount = 50; // number of millis/samples before a stable value

void setup()
{
    pinMode(buttonPin, INPUT_PULLUP);
    RGB.control(true);

    // Allow the buttons to know when the meter locks/unlocks
    Particle.subscribe("pc-b-lock-", mentoringSubscribe, MY_DEVICES);
}

void loop()
{
    if (mentoringMode)
    {
        // Non-blocking delay
        if ((millis() - blinkTime) >= (blinkRate / 2))
        {
            if (blinkOn)
            {
                // Turn off the LED
                RGB.color(0, 0, 0);
            }
            else
            {
                // Set the zone color
                switch (mentoringZone)
                {
                    case 1:
                        RGB.color(0, 0, 255); // Blue
                        break;
                    case 2:
                        RGB.color(0, 255, 0); // Green
                        break;
                    case 3:
                        RGB.color(255, 255, 0); // Yellow
                        break;
                    case 4:
                        RGB.color(255, 128, 0); // Orange
                        break;
                    case 5:
                        RGB.color(255, 0, 0); // Red
                        break;
                    default: // Also red.
                        RGB.color(255, 0, 0); // Red
                        break;
                }
            }

            blinkOn = !blinkOn; // Toggle
            blinkTime = millis(); // Reset delay
        }
    }
    else
    {
        // Update light color
        RGB.color(0, 255, 0);

        // Handle button presses
        if (millis() != lastButtonSampleTime) { // At most once per ms
            buttonReading = digitalRead(buttonPin);

            // If the old state equals the new state...
            if (buttonReading == currentButtonState) {
                // Keep buttonCounter >= 0
                buttonCounter = (buttonCounter > 0) ? (buttonCounter - 1) : 0;
            }
            else { // If the state has changed...
                buttonCounter++; 
            }

            // Stable value
            if (buttonCounter >= debounceCount) {
                buttonCounter = 0;
                currentButtonState = buttonReading;

                if (currentButtonState == LOW) {
                    Particle.publish("pc-trigger", String(buttonNumber), PRIVATE);
                    RGB.color(255, 0, 0);
                }
            }

            lastButtonSampleTime = millis();
        }
    }
}

// Takes both forms of the "pc-b-lock-?" event name
void mentoringSubscribe(const char* eventName, const char* zone) {
    String eventStr = String(eventName);
    if (eventStr.equals("pc-b-lock-y"))
    {
        mentoringMode = true;
        mentoringZone = String(zone).toInt();
        blinkTime = millis();
    }
    else if (eventStr.equals("pc-b-lock-n"))
    {
        mentoringMode = false;
    }
}
