# PC-O-Meter v2.0
## Automagical PC-O-Meter for the SSE Lab.

Uses a servo, RF communication, and a Raspberry Pi to indicate the current "political correct-ness" of the lab.

On each table, there is a large red button. When the button is pressed, the needle on the PC-O-Meter rises by a given amount, indicating that the lab has become less "PC" at that moment. After a cool-down period, the needle slowly lowers back to the baseline value.

Uses [WiringPi2](https://github.com/WiringPi/WiringPi2-Python) for the hardware PWM servo control, and RPi.GPIO for general GPIO.


### Wiring Diagram
![Wiring Diagram](http://i.imgur.com/MVKN4RK.png)
