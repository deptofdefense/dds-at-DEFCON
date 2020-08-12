# CircuitPlayground Software

## General Setup

Follow the [Adafruit tutorial](https://learn.adafruit.com/adafruit-circuit-playground-express) to get the board initially setup.  Make sure to update the bootloader and download any drivers that are needed.

Quick Reference:

* [Updating the bootloader](https://learn.adafruit.com/adafruit-circuit-playground-express/updating-the-bootloader)
* Update the CPX firmware:
  * For the ground station (stand alone CPX) : [Latest Circuit Playground Express](https://circuitpython.org/board/circuitplayground_express/)
  * For the Satellite (CPX+Cricket) : [latest CPX + cricket](https://circuitpython.org/board/circuitplayground_express_crickit/)
* [CircuitPython Libraries](https://circuitpython.org/libraries)

After setup, copy over the contents of either the [satellite](./cp-sat) or [ground](./cp-gs) onto the board.  To use the chatbot, run the [twitch code](./twitch/README.md) on a device connected to the ground station CPX over serial

## Challenges

### LEDs

| LED | Challenge | Notes |
| --- | --- | --- |
| 0 | Maintenance Password | Turns  yellow if they enter the normal password first |
| 1 | Secondary Control Antenna | Swings servo representing control antenna |
| 2 | Primary Control Antenna | Flashes the completed color before turning back to normal if they haven’t finished the secondary control antenna |
| 3 | Disable battery charging (Solar Panel 1) | Changes to the user position for a second before switching back if Primary Control antenna hasn’t been changed |
| 4 | Disable battery charging (Solar Panel 2) | Changes to the user position for a second before switching back if Primary Control antenna hasn’t been changed |
| 5 | Disable temperature controller | Will flash as a success for a second, before resetting if the primary control antenna hasn’t been changed |
| 6 | Override emergency failsafe | Lets them override the final settings |
| 7 | Update Orbit Parameters | Will be rejected while the flight systems are working, these get disabled by the failsafe override |
| 8 | Launch thrusters | Either cause the sat to spin or smoke |
| 9 | Free Play | User discovers one of the two free play command

### State Map

* 0: Default/Game Start
* 1: User has entered normal password
  * Return health status
* 2: User has entered maint password
* 3: Adjust secondary antenna
  * Set
  * Status
  * Calc 
* 4: Adjust primary antenna
  * Set
  * Status
  * Calc 
* 5: Disable Solar Panel 1 but not 2
  * Enable
  * disable
* 6: Disable Solar Panel 2 but not 1
  * Enable
  * disable
* 7: Disable both Solar Panels
* 8: Disable Temperature Control
  * Set
  * status
* 9: Override failsafe (orbit)
  * mode
* 10: Update orbit
  * Status
  * set
* 11: Launch thrusters
  * ignite
* 12: Free Play mode
  * Led
  * servo

#### CheatSheet

* !cmd login twitch_handle password
* !cmd login SpaceMaint 5p4c3d07c0m
* !cmd ant calc x y z
* !cmd ant set sec xyz
* !cmd ant set pri xyz
* !cmd bat disable pri
* !cmd bat disable sec
* !cmd temp status
* !cmd temp set -20 100
* !cmd orbit mode man
* !cmd orbit set inclination 2
* !cmd orbit ignite
* !cmd servo 1 45
* !cmd led 1 175 255 50

## Troubleshooting Notes

Very frustrating to be developing quickly with read/writes/executes to
a CircuitPlayground Express only for soemthing to hangup and the process
fail with an failed unmount or data corruption.

### Backup code

Back up `code.py` somewhere other than the Circuit Playground Express.

### Input/Output Errors

This happened a few times, here's what worked to reset the device.

```bash
# observe how the circuit mounted
dmesg

# if mounted with errors
umount /dev/sda1  # verify the correct device first (i.e. sda1)

sudo fsck /dev/sda1
```

### Clean Power Supply

Haven't done the math yet, but from observation the pi0 GPIOs being the exclusive power supply of the CPE, led diming was observed when sending commands
to change values along with intermittent soft reboots. It is therefore recommended that power to the CPE be provided from other than the pi0.
