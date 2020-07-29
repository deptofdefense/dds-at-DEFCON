# Simple Sat Hardware

## Ground Station Portion of CPX Simple Sat

Requirements to build and assembly a ground station portion of the SimpleSat kit are as follows: 

1. [Adafruit Circuit Playground Express](https://www.adafruit.com/product/3333)
2. [Raspberry Pi](https://www.amazon.com/CanaKit-Raspberry-4GB-Basic-Kit/dp/B07TXKY4Z9)
3. [Jumper Cables](https://www.adafruit.com/product/1953) or [Alligator clips](https://www.adafruit.com/product/1008)
4. (Optional - current GS frame is built for this case) [Aluminum Pi 4 case](https://www.amazon.com/Geekworm-Raspberry-Computer-Aluminum-Compatible/dp/B07VD6LHS1/)

## Satellite Portion of CPX Simple Sat

Requirements to build and assemble a Satellite portion of the SimpleSat kit are as follows:

1. [Adafruit Circuit Playground Express](https://www.adafruit.com/product/3333)
2. [Adafruit CRICKIT for Circuit Playground Express](https://www.adafruit.com/product/3093)
3. [Power Supply for CRICKIT](https://www.adafruit.com/product/276)
4. STL files 3D printed to the quantity specified below.
5. Nuts and bolts outlined below.

## Simple Sat Enclosure

### STL Files

Print the .stl files in the following quantity:

1. sat_upper_half - 1
2. sat_lower_half - 1
3. sat_solar_panel_arm - 2
4. sat_solar_panel - 2
5. sat_solar_panel_gear_18 - 2
6. sat_radar_dish_arm - 2
7. sat_radar_dish - 2

### Hardware Requirements

| Item | Quantity |
| ---- | -----    |
| M2.5x10 Bolt    | 8 |
| M2.5 Nut        | 8 |
| M2.5x20 Bolt    | 4 |

Alternatively, it may be cheaper and easier to simply purchase an assortment of M2.5 nuts and bolts.

[Example Kit](https://www.amazon.com/HVAZI-Metric-304-tornillos-inoxidable/dp/B07F14J7X8/ref=sr_1_21?dchild=1&keywords=hvazi+m2.5+304+button+head&qid=1591969674&sr=8-21)


In addition, the screws that came with the Micro Servos are also used to affix gears to them and to secure the motors in place.

## Assembly Instructions

### Servo Orientation

The following diagram depicts the intended servo orientation when fully assembled.

<pre>
                               -------
                              /       \
                             /         \
                            | Servo #4  |
                            |           |
                             \         /
                              \       /
                               -------
                                  ||
                                  ||
                          |---------------|
|---------------------\   |           PWR |   /---------------------|
|                      \--|               |--/                      |
|      Servo #1           |               |           Servo #2      |
|                      /--|               |--\                      |
|---------------------/   |               |   \---------------------|
                          |---------------|
                                  ||
                                  ||
                               -------
                              /       \
                             /         \
                            | Servo #3  |
                            |           |
                             \         /
                              \       /
                               -------
</pre>
