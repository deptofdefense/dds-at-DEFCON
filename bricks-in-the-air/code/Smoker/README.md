# Fogger

The fogger is basically a mini improvised fog machine made out of an eSig. It uses fog juice just like a regular fog machine would. The eSig holds the heating coil to vaporize the fog juice. 

This project uses lithium batteries and decently high current (~2-4A) so care should be taken in making this. You are heating a coil up hot enough to boil off fog juice. A controller board has been made to help increase safety but it's up to you to take the necessary precautions and make sure the project is within your skill level to complete safely. You do so entirely at your own risk and no liability his held by any other person or organization. 

Ok, now that that is out of the way let's get to it. 

### Parts
Here are the parts and equipment you need for this project. You can get the parts from anywhere, links to in stock sources at the time of writing have been included for ease. Note, do not substitute the eSIG, or FET without proper analysis to select appropriate replacement components by someone capable of circuit design.  

You will also need several basic tools such as wire strippers, pliers, drill, and a soldering iron with solder. Walk through the instructions below for details of what will have to be done.

| Item | QTY | Example Link to Source |
|----------|----------|-------|
| Kanger Tech T2 Ego eSig |	2 |	[Vaping Zone](https://www.vapingzone.com/kangertech-t2-ego-clearomizer-single-pc.html) |
| Fog juice	| 1	| [Amazon](https://www.amazon.com/FogWorx-Extreme-High-Density-Juice/dp/B0777S56RB/ref=sr_1_5?dchild=1&keywords=fog+juice&qid=1593553743&sr=8-5) |
| Air Pumps W/Tubing | 1 | [Amazon](https://www.amazon.com/gp/product/B06Y2CXZ67/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1) |
| 18650 Batteries W/Charger	| 1 |	[Walmart](https://www.walmart.com/ip/EBL-4-Pack-3000mAh-3-7V-Rechargeable-Batteries-Battery-Charger-for-Li-ion-18650-18500-14500-Replacement-Battery/148568497) |
| Wire |	1 |	[Amazon](https://www.amazon.com/Electrical-Flexible-Silicone-different-automotive/dp/B07G744V5Z/ref=sr_1_5?dchild=1&keywords=wire&qid=1593557372&sr=8-5) |
| Shrink Tubing	| 1	| [Amazon](https://www.amazon.com/650pcs-Shrink-Tubing-innhom-Approved/dp/B07WWWPR2X/ref=sr_1_8?dchild=1&keywords=shrink+tubing&qid=1593557287&sr=8-8) |
| FETs (IRLU8743PBF-ND)	| 2	| [Digikey](https://www.digikey.com/product-detail/en/infineon-technologies/IRLU8743PBF/IRLU8743PBF-ND/1894174) |
| Resistors (10K) |	2 |	[Digikey](https://www.digikey.com/product-detail/en/stackpole-electronics-inc/CF14JT10K0/CF14JT10K0CT-ND/1830374) |
| Diodes (P600M-E3-54GICT-ND) |	1 |	[Digikey](https://www.digikey.com/product-detail/en/vishay-semiconductor-diodes-division/P600M-E3-54/P600M-E3-54GICT-ND/3025895) |
| Arduino Mini Pro 5V 16MHz |	1 |	[Sparkfun](https://www.sparkfun.com/products/11113) |
| USB FTDI Breakout |	1 |	[Sparkfun](https://www.sparkfun.com/products/9716) |

### PCB
The PCB is optional and currently in alpha state meaning it has been designed but not yet manufactured and tested. The circuits are simple and can be assembled without a PCB, but it does make things neater and easier. 


![](Images/Fogger_Power_CTRL.png)


![](Images/Fogger_Power_CTRL-PCB.png)


![](Images/Fogger_Power_CTRL-SCH.png)

The PCB has been designed to be easily made at home either via etching or isolation routing.  

There is also an interactive Bill Of Materials (BOM). Just open the web page and it will highlight the parts selected making it easy to assemble and trace out circuit paths.  


![](Images/Fogger_Power_CTRL-BOM.png)

All the PCB files can be found in the PCB folder in this repo. It was designed using KiCAD which is free and open source tool so that everyone has access to the source files for modification.  

**IMPORTANT**  
The only thing that is easy to mess up that could cause damage is inserting the diode incorrectly. Make sure the stripe is facing the correct way as indicated in the photo above. Inserting it backwards will cause a short across the diode when the motor is engaged which can cause components to heat up and potentially cause a fire. Please pay attention to this!


### eSig Modification
This section will walk you through modifying the eSig and connecting the wires needed to drive the coil in it. Originally the T2 is designed to connect to a controller that applies power to it. We are making our own controller in substitution of this. 

**Step 1**
- This is what the eSig looks like fresh out of the package

![Step 1](Images/S01-Package.png)

**Step2**
- There are two breather holes on the side. We will be passing one of the wires through one of the holes.
- You will need to widen the hole slightly. The goal is to make it just big enough for your wire to fit through, without tearing into the insulation.
- If you make the hole too big, don't fret, you can use hot glue, silicone, or other sealant to seal the hole up after. 

![Step 2](Images/S02-Drill.png)

**Step 3**
- After passing the wire through the hole, strip off the end and solder it to the middle post
- IMPORTANT:
  - Do not cover the hole with solder or the wire. Air must be able to pass through the hole.
  - Do not let the solder or un-insulated part of the wire touch the outside ring or base, only the middle post. The middle post is one contact of the coil while the outside ring is another. If you do short them, when you turn your smoker on your wires will get very hot and components will be destroyed. 
  - If you are unsure you can use a multimeter to measure the resistance between the wire and the ring. It should be 1.8 ohms or above. If it's lower, you most likely have a short.

![Step 3](Images/S03-Solder.png)

**Step 4**
- Here you will cover the second hole to prevent air leaks and use that cover to connect the second wire
- Use something sharp to scrape off the chrome plating so that solder will stick to it.

![Step 4](Images/S04-Scrape.png)

**Step 5**
- Solder the second wire to the plug
- You can now take the mouthpiece off the second eSig and place it on the back of your smoker. 
![Step 5](Images/S05-Solder.png)

Congratulations, your modified eSig is now ready for the electrical assembly. 

### Electrical Assembly (No PCB)
While a PCB design is underway to make assembly easier, the control circuit has also been designed so that you don't need to make a PCB to create the Smoker.

**Step 1**
- Attach the Resistor to a FET as shown
- This is a pulldown resistor that keeps the FET off while the trigger line is floating

![Step 1](Images/01-FET-Resistotr.png)

**Step 2**
- Remember when connecting things to put the heat-shrink on the wire before soldering so you can slide it down and heat it up to secure it. If you forget, you will have to pull the wire off and re-solder it all over again.

![Step 2](Images/02-Smoker-shrinktubing.png)

**Step 3**
- Solder one of the blue wires (preferably the one connected to the outside of the unit plunging the hole) to the middle terminal on the FET.

![Step 3](Images/03-FET%20Soldered.png)

**Step 4**
- Move the heat shrink up making sure that there is no exposed wire or solder that could touch the other two contacts. 
- Use a heatgun to shrink the tubing.

![Step 4](Images/04-FET%20Shrinktubed.png)

**Step 5**
- Solder a green and black wire to the other two connectors
- The FET is still face up in this image, the green wire is connected to the left pin while the blue to the right.
- Cover the whole assembly with shrink tubing to protect it.

![Step 5](Images/05-FET-all-soldered.png)

**Step 6**
- The pump has a red dot next to it's positive terminal
- Wrap the diode around the two terminals as shown
- IMPORTANT
  - The diode MUST be put on in the right direction. The silver line must be pointing to the positive side.
  - Make sure the metal terminals do not contact the metal casing.
  - If this is put on backwards you will get a nice pop out of the diode as it heats up to red hot conditions. 
- Connect a red and black wire to the the positive and negative terminals as shown. 
- Shrink tube to cover and protect the contacts.

![Step 6](Images/06-Pump.png)

**Step 7**
- Assemble the second FET just like you did the first FET with the pulldown resistor.
- Connect the negative (Black) wire to the center post of the FET.
- Connect a green wire to the left and a black wire to the right pins as shown
- When done, place a piece of shrink tubing over the FET to protect it.

![Step 7](Images/07-FET-Pump.png)

**Step 8**
- Connect the two negative (Black) wires together as shown
- Connect the two positive (Red and Blue) wires together as shown

![Step 8](Images/08-Combining.png)

**Step 9**
- Solder the negative and positive wires to the negative and positive terminals of the battery (Do this with NO battery installed)
- IMPORTANT
  - Be sure to get the polarity correct and don't mix up positive and negative. There are markings on the inside of the battery holder but they are small.
  - If you need to add labels to the battery holder to make sure your battery gets inserted correctly.
  - If you put the battery in backwards the smoker and motor will automatically turn on, the motor will run in reverse, and the FETS will likely be damaged if left on for too long.
  

![Step 9](Images/09-Battery%20Soldered.png)

**Step 10**
- Time to test the smoker before connecting to the controller!
- Add some fog juice to the smoker by removing the top mouthpiece.
- Add a section of tubing from the pump kit to connect the pump to the eSig.
- Allow time for the wick to soak up the juice, you can shake it up a bit to help it but not too much.
- Make sure the smoker is pointing upward. Ideally even more upright than in this image.
- The two green wires are trigger wires. You can connect them to the positive side of the battery to turn the circuit on to test it. 
- If you hear crackling from the smoker but it's not putting much out, the wick got too wet. (You did keep it upright, right?) If that happens you can blow into the mouthpiece (with it off!) and a few drops of fluid will be pushed away from the coil. Try it again, it should now smoke

![Step 10](Images/10-Test.png)


### Connecting the Controller
This section is in progress and needs some photos but luckily the steps are not too hard and I have faith you can figure these out in the mean time. 

![Arduino Pro Mini](Images/Arduino%20Pro%20Mini.jpg)

- Be sure you removed the battery before continuing
- Solder on a black wire to the negative side of the battery
- Connect the other side of that wire to the GND pin of the Arduino Pro Mini (Either one of the two listed above will work)
- Solder on a red wire to the positive side of the battery
- Connect the other side of that wire to the VCC pin of the Arduino Pro Mini
  - Note: Make sure you did buy the 5V version of the Arduino Pro Mini. If not, powering from the battery on VCC will cause damage!
  - Note, the Arduino Pro Mini is rated to be run at 5V. However, a fully charged LI-ION battery like the 18650 we have has a max voltage of about 4.2V. The battery can drain as low as 3.5V on average. In testing, the Arduino Pro Mini operates stability as far down as 2.2V. So powering VCC directly from the battery should be sufficient.
  - If you are wondering why not pick the 3.3V version of the Arduino Pro Mini and power through the RAW pin which has a regulator to run everything at 3.3V, then you are clever but there is one gotcha. The FET resistance at a gate voltage of 3.3V is much higher than that of the 4.2V. In order to simplify the circuitry and reduce FET heat output, we are maximizing the gate drive voltage. As the Arduino was stable at much lower voltages, this we the simplest compromise. 
- Connect the green wire that controls the Pump to Pin 10 of the Arduino
- Connect the green wire that controls the eSig to Pin 11 of the Arduino
- Connect a black wire to the other GND pin of the Arduino
- Connect a wire of your choosing to pin 9 of the Arduino.
  - This is your trigger pin
  - When this pin goes high, the smoker will run for the specified amount of time
  - IMPORTANT
    - This pin has no pulldown resistor on it, so if it's not connected to a signal source, it will repeatedly trigger the fogger. 
    - You can either add a 10K resistor between the GND wire and the trigger line, or make sure the line is connected to the source signal that will drive it high and low as needed.
    - It's up to you to design what this is connecting to and how you trigger it. A simple way would be connect a button to the trigger line that connects it to VCC when the button is pressed (remember to add that resistor to pull it back down when the button is not being pressed).
    
Wiring is now done! Congratulations!

### Programming and Configuring the fog controller
The Arduino Pro Mini must now be uploaded with the firmware. 
There are lots of good tutorials for hooking up the Aruino Pro Mini and configuring the Arduino IDE.   [Here is one](https://www.arduino.cc/en/Guide/ArduinoProMini)  

The Basic FTDI board in the parts list was used to program and configure the board.
![FTDI Basic Board](Images/FTDI.jpg)

The code is located in this folder inside of the Code directory.

The controller has configurable parameters that can be adjusted. The parameters will be remembered even if the battery is disconnected and the board is restarted. To configure the board, use the serial terminal in the Arduino IDE. When opened, you should see the following instructions printed out in the terminal. 

Good luck and have fun!


```
Saved State Found, populating settings
 
Instructions:
The first letter is the command
The numbers following the letter (if applicable) is the setting
For example p50 will set the pump to 50% duty
Warning, it's up to you to make sure you supply adiquate air
for the fog level. You also need to make sure you don't run 
the fogger too long or you can cause a hazardus condition. 
Make sure you allow enough cooldown time also.
Fogger control pin is : 11
Pump control pin is : 10
Trigger pin is : 9
 
Default Settings:
Pump % = 255
Fog % = 255
Run time [s] = 20
Cooldown time [s] = 5
 
Current Settings:
Pump % = 255
Fog % = 255
Run time [s] = 5
Cooldown time [s] = 1
---------------------------------------------------------------
P### - Set pump speed %     (range 0-255)
F### - Set fog level %      (range 0-255)
R### - Max Run Time Seconds (range 0-255)
C### - Set Cooldown time    (range 0-255)
D    - Reset all to default
T    - Manually Trigger Fogger

```


# Future Improvements
- 3D print a tube adapter for the back so that you don't need two eSig's to make one smoker
- Add images of the controller wiring
- Improve the programming and settings walkthrough
- Add schematic and PCB for the smoker circuit