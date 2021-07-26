# Arduino Files

Basic functional board setup:
  - 3 ATmega328/Arduinos interconnected through I2C.
  - Each Arduino has 
    - 3 LEDs for discrete signals
      - Green LED - Digital Pin 3 (PD3)
      - Yellow LED - Digital Pin 5 (PD5)
      - Red LED - Digital Pin 6 (PD6)
    - 1 IR LED for interaction/driving the Lego Power function IR. - Digital Pin 10 (PB2)
      - [https://github.com/jurriaan/Arduino-PowerFunctions](https://github.com/jurriaan/Arduino-PowerFunctions)
    - Serial RX on Digital Pin 0 (PD0)
    - Serial TX on Digital Pin 1 (PD1)
    - I2C connectivity via standard SDA(PC4)/SCL(PC5) Pins
    
## Documentation for I2C Address assignments
Engine Control Unit - 0x54

## Documentation for Solutions
We need to have solutions avaialble for the people volunteering in the booth so that they can help people work through a given solution.
    
## To do/Ideas

1. Program a .ino that acts as the Mission Computer/Flight Controller. Design this as the Master on the bus that queries and sets the various other controllers.
2. Program a .ino that controlls the Landing Gear
3. Program a .ino that controlls the aircraft lights

4. Start thinking about unique challenges that escalate in complexity. For instance, the Engine can't be stopped from Ludacrous speed, it has to slow down first. Only let Landing gear lower if the engine speed is less than speed 6. The sky is the limit here for complexity. It will be a balancing act between letting someone learn something brand new in 10 minutes or letting an expert dive deep for 5 hours. There will be 5 Lego kits available and ~10 boards for people to be using and interacting with. Time permitting, consideration should be made to make the challenges increasingly difficult.

5. We need to develop/maintain/make available "documentation" for our design such that a person learning the system could read and understand our ICD/SDD for the various components so that they can start to interact with the Lego airplanes.
  
  
