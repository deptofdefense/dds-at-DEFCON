# CPX SimpleSat Assembly Guide

## Parts needed

### 3D Printed pieces

Essential parts:

* 2 Solar Panel Arms
* 2 Solar Panels
* 2 Antenna Dishes
* 2 Antenna Arms
* 2 Servo Gears
* 1 Satellite Upper body
* 1 Satellite Lower body

Nonessential parts, but needed if doing smoker modification:

* 1 Smoker upper shell
* 1 smoker lower shell

### Commerical Parts

Essential parts:

* [Screw kit](https://www.amazon.com/DYWISHKEY-Pieces-Stainless-Socket-Washers/dp/B082XPZV1V)
* [Micro Servo](https://www.amazon.com/Micro-Servos-Helicopter-Airplane-Controls/dp/B07MLR1498/)
* [Adafruit CRICKIT](https://www.adafruit.com/product/3093)
* 2x [Circuit Playground Express](https://www.adafruit.com/product/3333)
* Raspberry Pi

For Smoker modification:

* [Diminus mini air pump](https://www.amazon.com/gp/product/B06Y2CXZ67/)
* 1/4" silicone tubbing
* 2 KangerTech T2 esig

## Build instructions

### Satellite

The satellite part of CPX Simple Sat is the most complicated part of the build, so we'll tackle that first.  Note the satellite will function with or without the smoke kit, so it's your choice if you want to add it.  

| Build Steps |
| --- |
| ![inital parts](./photos/IMG_20200730_125532.jpg) |
| Here are all the parts we'll need to build the satellite.  Note for this build we painted the central part of the satellite gold to mimic the look of the multi-layer insulation on most satellite.  |
| ![smoke holes](./photos/IMG_20200730_125548.jpg) |
| Here are the holes drilled to allow the smoker to produce smoke from underneath the CRICKIT board.  This step isn't required, but it does make it look cool |
| ![ant servo](./photos/IMG_20200730_125650.jpg) |
| For the first part of the build, we'll put together the antenna controller arms. Make sure all the micro servos spin smoothly before assembly|
| ![ant](./photos/IMG_20200730_130027.jpg) |
| Find the side of the arm that has divots.  this will be the top of the arm |
| ![ant](./photos/IMG_20200730_125813.jpg) |
| To start, run the servo cable through the cavity within the arm |
| ![ant](./photos/IMG_20200730_130114.jpg) |
| After sliding the micro servo into the gap, lock it in place by screwing it in using one of the small screws that came with the micro servo |
| ![ant](./photos/IMG_20200730_130208.jpg) |
| Now snap on the the antenna dish.  The hole at the bottom of the dish should be a snug fit for the white gear on the servo.  If it feels loose, use another screw from the micro servo kit to make it a tighter fit |
| ![ant](./photos/IMG_20200730_130523.jpg) |
| After making both control antenna arms, lets move onto the solar panels.  First find the solar gears and push them onto the two remaining micro servos, just like we did with the antenna dish |
| ![ant](./photos/IMG_20200730_130710.jpg) |
| After doing this twice, you've now finished assembling your servo components |
| ![smoke](./photos/IMG_20200730_131106.jpg) |
| ![ant](./photos/IMG_20200730_131213.jpg) |
| This step is optional but if you drilled holes for the smoker, now would be a good time to attach part of the tubing to the front panel.  The more flush the tubing is to the hole, the more even the spread of smoke.  I like to use hot glue to hold this end of the tubing in place while we assemble everything else |
| ![ant](./photos/IMG_20200730_131338.jpg) |
| ![ant](./photos/IMG_20200730_131358.jpg) |
| Now would also be a good time to measure out how much tubing you will need to route through the satellite.  Give your self a little extra to play safe, and then cut off the extra tubing | 
| ![ant](./photos/IMG_20200730_131543.jpg) |
| Now route the servo cable from the antenna arms through the back of the front panel |
| ![ant](./photos/IMG_20200730_131815.jpg) |
| Using 10mm screws, attach the antenna arms to the front panel.  Make sure everything is facing the right direction |
| ![ant](./photos/IMG_20200730_133945.jpg) |
| ![ant](./photos/IMG_20200730_133952.jpg) |
| Using a nut, lock the arm in place on the other side.  You can also use spacers between the arm and panel, as well as the nut and panel to stop the screw from digging into the pla if you tighten to much |
| ![ant](./photos/IMG_20200730_135255.jpg) |
| repeat with the second arm |
| ![ant](./photos/IMG_20200730_135632.jpg) |
| Now we will install the micro servos that will control the solar panels. |
| ![ant](./photos/IMG_20200730_135716.jpg) |
| ![ant](./photos/IMG_20200730_135913.jpg) |
| ![ant](./photos/IMG_20200730_140052.jpg) |
| I like to use hot glue on the back of the servo to help hold it in place.  A small drop where the gap that the cable exits from is enough |
| ![ant](./photos/IMG_20200730_141603.jpg) |
| Now its time to build the smoker backpack.  Note the side with the deeper opening for the pump is the bottom of the backpack |
| ![ant](./photos/IMG_20200730_143236.jpg) |
| ![ant](./photos/IMG_20200730_143240.jpg) |
| Using four 6mm screws, attach the backpack to the rear panel |
| ![ant](./photos/IMG_20200730_143349.jpg) |
| ![ant](./photos/IMG_20200730_144517.jpg) |
| Using four 16mm screws attach the cover of the backpack.  Note the two pieces are not supposed to go flush together.  There should always be a gap between them |
| ![ant](./photos/IMG_20200730_145429.jpg) |
| Now its time to attach the cricket board |
| ![ant](./photos/IMG_20200730_150800.jpg) |
| Before you attach the crickit to the front panel, you may want to do some cable management to clean things up.  Also note that the two solar panel servos should go in servo slots 1 and 2, while the two antenna servos should go in slots 3 and 4 |
| ![ant](./photos/IMG_20200730_151001.jpg) |
| ![ant](./photos/IMG_20200730_151125.jpg) |
| Depending on how much clearance you want for the smoke use either four 25mm or 20mm screws to attach the crickit to the satellite.  Use nuts to both keep the crickit steady and lock in its offset from the surface of the satellite |
| ![ant](./photos/IMG_20200730_151905.jpg) |
| ![ant](./photos/IMG_20200730_152146.jpg) |
| We're almost there.  Go ahead and slide the panels into the notches on the arms to complete their build.  Then you will want to place them on the bottom panel and line it up with the top panel.  Make sure to route the smoker tubing through the back panel if you are using that design.  Finally screw everything together with four 25mm screws.
| ![ant](./photos/IMG_20200730_152659.jpg) |
| ![ant](./photos/IMG_20200730_152750.jpg) |
| The next steps are for getting the smoker integrated with the satellite.  First tape the mosfet and extra cables to the back of the satellite to keep it out of the way. |
| ![ant](./photos/IMG_20200730_153138.jpg) |
| Attach the air pump cables to DC motor 1 on the crickit |
| ![ant](./photos/IMG_20200730_153819.jpg) |
| Attach the smoker cables to the 5V and ground lines of the neopixel terminal.  We use this terminal because most of the cricket lines are only designed for 3V and limited current.  The smoker is a fairly demanding heating element, so by using the neopixel terminal we can get the voltage and current we need without hampering the rest of the board |
| ![ant](./photos/IMG_20200730_153912.jpg) |
| Plug a pin into the signal 1 line of the I/O connector.  I prefer to just use a male jumper cable and then solder it to the signal cable on the smoker |
| ![ant](./photos/IMG_20200730_154429.jpg) |
| ![ant](./photos/IMG_20200730_154647.jpg) |
| Here we solder and heat shrink the jumper cable |
| ![ant](./photos/smoke.gif) |
| And now you test it out.  If all went well you will have a working CPX Simple Sat.  Congratulations! |
| Note if you want to make the satellite look better in the dark, cover up the green power leds with tape |

### Ground Station

| Ground station setup |
| :---: |
| ![gs](./photos/cpxground.jpg) |
| Building the ground station part is straightforward.  The two pieces slot together, and if using a case like [this](https://www.amazon.com/Geekworm-Raspberry-Computer-Aluminum-Compatible/dp/B07VD6LHS1) it should fit snugly on the pi.  Once there, either screw/hot glue/tape the cpx to the board and connect the 3.3V, GND, TX, and RX to the pi or whatever device the chatbot is running on.  