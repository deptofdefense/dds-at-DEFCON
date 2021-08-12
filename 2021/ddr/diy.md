# How to make your own rover

This is a guide on how to make your own version of the defense digital rover.  We'll go over the hardware, 3D printed files, and software needed.  Feel free to use everything to either recreate the rover we made, or spin off and make your own thing.  

## Hardware

The hardware list for the rover is fairly light and consists of the following:

* [Bogie Runt Rover](https://www.servocity.com/bogie-runt-rover/)
  * Be careful where you order the kit from, some amazon sellers like to markup the price by a lot
* [Raspberry Pi 4](https://www.sparkfun.com/products/15447)
  * In our setup we don't use the pi to run OBS, so any model will work.  If you want to simplify the design and run OBS within the rover, use one of the versions with more ram so that you can run both OBS and the rover python script
* [Raspberry Pi HQ Camera Module](https://www.sparkfun.com/products/16760)
  * We liked the smaller form factor of the new pi camera module, so we used this one.  Feel free to use a webcam if you already have one
* [Raspberry Pi HQ Camera Lens - 6mm Wide Angle](https://www.sparkfun.com/products/16762)
  * We chose this lens because it was the cheaper of the two that come with the camera module, feel free to use a different lens if you want to
* [SparkFun Auto pHAT](https://www.sparkfun.com/products/16328)
  * This is the motor controller for the rover.  It has a lot of extra features like servo controllers and a 9DoF sensor we don't use, but maybe next year we'll get to really push the board.  Note that there is a small trace near the USB C port labeled Pi ISO that you will need to cut.  This will force you to power both the pi and hat separately, but will get rid of the low voltage warning.  If you don't cut this trace, you will see a low voltage warning when you plug in the pi, and the pi will sometimes reset when the motors are running at full speed.
* [Amperka Octoliner](https://www.amazon.com/gp/product/B081P833RK)
  * This is the line sensor we used to keep the rover in the play area.  It's a great sensor when your carpet is a nice solid color and not an art piece
* [Anker PowerCore+ 26800mAh](https://www.amazon.com/gp/product/B07XRJZXKY)
  * This is the battery pack that we used.  It's overkill for the rover because we originally planned on running the rover 24 hours a day and just swap the battery in the mornings.  
* [Tripod Screw Adapter](https://www.amazon.com/gp/product/B079BNWB6K)
  * This is used to hold the pi camera in place.  
* [MatterHackers Silky Gold Filament](https://www.matterhackers.com/store/l/silky-gold-mh-build-series-pla-filament-175mm-1kg/sk/MAQNPYVJ)
  * This is the filament we used to print the 3D printed parts.  It's a great filament for printing, and it's not too expensive.  It also has a really nice finish that makes the rover look real.  
* [Raised3D Black PLA](https://www.matterhackers.com/store/l/raise3d-premium-pla-filament-175mm-1kg/sk/MQ39QDEN)
  * This is the filament we used for the fake solar panels on the roof of the rover.  You can use any black filament that you prefer, we just had this on hand.  

## 3D printed parts

All the parts were printed in PLA on a [Raised3D E2](https://www.raise3d.com/products/e2/).  Note that pretty much any printer will work for these parts, you do not need an expensive or large printer to print them.  

We used the Silky Gold filament for the external parts, because it gave the rover a realistic look.  The solar panel pieces were printed in black, and the internal pieces were printed in whatever colors we had loaded at the time.  

This is the list of printed parts we used:

* 1x [Line Sensor mount](./3dFiles/bar.stl)
  * This is used to mount the line sensor to the bottom of the rover.  In our case, we mounted it in between two of the rovers wheels. 
* 1x [Battery Holder](./3dFiles/batteryHolder.stl)
  * This is used to hold the battery in place inside the rover.  It should be a tight enough fit that the battery doesn't fall out of the rover.
* 1x [bumper](./3dFiles/bumper.stl)
  * This is used to extend out the bumber on the bottom of the rover.  It's a bit of a hack, but it works.  This is needed because the battery pack is very long, and otherwise it sticks out of the back.  
* 1x [camera mount](./3dFiles/cameraMount.stl)
* 1x each of the outer panels in silky gold:
  * [camera panel](./3dFiles/cameraPanel.stl)
  * [left panel](./3dFiles/leftPanel.stl)
  * [right panel](./3dFiles/rightPanel.stl)
  * [spacer](./3dFiles/spacer.stl)
  * [battery panel](./3dFiles/end.stl)
  * [cover frame](./3dFiles/coverFrame.stl)
* 4x any combination of the following mock solar panels:
  * [alien panel](./3dFiles/cover-coverAlien.stl)
  * [single antenna panel](./3dFiles/cover-coverAntSingle.stl)
    * 1x [antenna](./3dFiles/cover-antenna120.stl)
  * [double antenna panel](./3dFiles/cover-coverAnt.stl)
    * 2x [antenna](./3dFiles/cover-antenna120.stl)
  * [plain cover](./3dFiles/cover-plain.stl)
* 8x [peg](./3dFiles/peg.stl)
  * These are used by both the camera panel and bumper to hold everything in place while gluing things together.
* 6x [long peg](./3dFiles/longPeg.stl)
  * These are used by the batter panel and spacer.

## Software

One key thing to note is that [TwitchIO](https://github.com/TwitchIO/TwitchIO) is used to connect to the Twitch streams.  For the version played at defcon, we used TwitchIO version 1.2.3 to connect to the twitch streams.  This version is incompatible with the newer version 2.0 of the API.  I will be releasing a 2.0 compliant version soon, but for now keep in mind that you will need to use an older version of that API.  

The rover is controlled by running [driverBot](./sourceCode/driverBot.py), which handles controlling the rovers' chatbot and driving the rover around.  The ground station is controlled by running [gsBot](./sourceCode/gsBot.py) on whichever computer will be running OBS.  This can be a laptop or even another pi.  The reason we run OBS on a separate computer is that it is easy for the pi to get overwhelmed when doing scene changes in OBS.  The rover has four of those, represented by the theme command options.  
