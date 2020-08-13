# DDSAT-1

Created as a part of the [Aerospace Village](https://aerospacevillage.org/) for DEFCON28, DDSat-1 attempts to teach the basics of RF exploitation and injection over Twitch IRC chat.  What could go wrong?  

| ![ddsat](./photos/MVIMG_20200807_100413.jpg) |
| :---: |
| There is a reason satellites aren't made out of plywood |

## Background

More often than not, when attempting to interact with space and air based systems one does so via different Radio Frequency (RF) data links.  As such a key part of this space is understanding how to recognize, reverse, and exploit different RF data links to cause effects on a target.

With DDSat-1, we are replacing the actual RF portion of the signal with a base64 encoded data stream.  This is because sending and receiving raw RF data over the internet is a bandwidth intensive task.  However the rest of the messages, from the encoding to formatting are based on real world data links.  Within the stream one chatbot, 0773rb07, acts as the ground station sending messages to the satellite using the `!msg` command.  The satellite chatbot is using the DDSat1 channel and responds with `!rsp`.  DDSat1 also periodically generates status messages that are tagged with `!status` in chat.  

### RF Demon Magic 101

Before we go deeper into what the formatting DDSat looks like, lets discuss the basics of RF from an exploit standpoint.  The first thing to note is that most RF data links fall into two broad families, symbolic and interpretative data links.  In a symbolic data link the message length and size tend to be static, with the layout of all possible messages hard coded into the ICD.  On the other hand, an interpretative data link will have messages of varying sizes and the ICD will usually identify one or more free text fields. A classic example of a symbolic data link is ADS-B, while an example of an interpretative data link would be ACARS.

Symbolic data links tend to be safer from the standpoint of having more well defined states and less risk of an unknown edge case.  However symbolic data links are difficult to update or add new features to, by their nature any new bit or field requires the radio code to be rewritten.

Interpretative data links are prone to unexpected edge cases, because it can be difficult for the programer to account for every possible message their program may receive.  However the difficulty testing for message behavior is offset by the ease of adding new fields or data to the message.  Unlike a symbolic data link, an interpretative data link can add new fields to a message without having to touch or alter the underlying code controlling the radio.  

Regardless of which data link family you find yourself dealing with, it's important to remember that most data links have no way to externally validate a message, and encrypting RF data links is still a rare occurrence.  This means that as long as you look and sound like a valid message, your target will likely act on your commands as if you were one.

One other concept to be aware of is multipath propagation.  When a message is transmitted out of an antenna, it tends to do so in an omnidirectional pattern.  That means that instead of traveling in a narrow line to the target, the message is actually radiated in all directions.  Depending on the environment this means that the message may reach the target multiple times due to reflecting off of different surfaces.  The common solution to this problem is to add a counter to the message that increments as the transmitter and receiver send data back and forth.  

When first looking at a signal it can be hard to tell if there is a counter field.  The quickest way to test for one is to simply rebroadcast an old transmission with a known behavior.  If the target acts on the command, congratulation your free to rebroadcast and inject commands at will.  If it doesn't than that means there is likely a counter somewhere near the start of the message, and you need to look for patterns in the data.  

## The Design

### RF

Now that we've gone over the basic background, lets look at the actual design decisions that made DDSat what it was.  To allow for rapid development, it was decided early on that DDSat would be an interpretative data link.  That allowed for more flexibility and allowed for more rapid changes to the message format.  

One thing that I forgot to mention earlier was the concept of encoding.  Not exclusive to RF, encodings are used any time a data link has a risk of transmitting a stream of all zeros or ones without a clock or reference signal.  It's a classic data link problem with many different solutions.  If we were doing this in the real world, the DPSK modulation would take care of this for us, so we could technically skip this step.  But for added complexity I added in a manchester encoding onto the data.  That means before it is converted into base64, every `1` is replaced with a `10` and every `0` with a `01`.  Manchester is an old encoding scheme with an easy to recognize pattern, which hopefully means everyone figured it out quickly.

To make this easy to read and identify, it was decided to use ascii characters as often as possible.  As such, the characters `C`, `R`, and `S` were picked to act as message type identifiers, while the target and payload fields were also to be kept in ascii.  

In addition to a dynamic payload, it was decided to use CRC32 for message validation.  While not that common in actual RF signals, its a popular enough standard in digital communication that people would recognize it easier than some of the real world versions.  

#### The Formatting

All message types have a common header with the following format:

| Message Type | Command Number | Payload length |
| :---: | :---: | :---: |
| The character `C` if a command message, `R` if a response to a command, or `S` if a status message.  Size: 1 byte | A number from 0 to 255 that increments each time a command is acted on.  The satellite will act on command numbers up to the next number it has stored + 25.  Size: 1 byte | The length of the payload field in bytes.  In addition to hinting that this is an interpretative message, this field was also meant to help show the cut off between the payload and CRC field.  Size: 1 byte

For command messages, the payload field is actually split into 2 fields.  A target field, which is always 5 bytes and identifies which of the 5 subsystems the message is addressing, and a payload field that contains the actual command.  The five subsystems are:

* `PAY01` : the left circuit playground express
* `PAY01` : the right circuit playground express
* `BAT01` : the left solar panel
* `BAT02` : the right solar panel
* `CAM01` : the top camera

For `CAM01`, `BAT01`, and `BAT02` the payload is expected to begin with `A`, for angle, and then a number from 0 to 180 that represents the angle in degrees to set the servo to.

For `PAY01` and `PAY02`, there are 3 different types of payload commands: 

* L
  * reads the light level from the payload and updates the status message with it
* T
  * reads the temperature of the payload and updates the status message
* Color settings:
  * A
    * Sets all of the neopixels to the given color
  * U
    * Sets the upper 5 leds to the given color
  * B
    * Sets the bottom 5 leds to the given color
  * 0 through 9
    * sets the specific led to the given color
  * Valid colors:
    * RED
    * ORANGE
    * YELLOW
    * GREEN
    * CYAN
    * BLUE
    * INDIGO
    * VIOLET
    * PURPLE
    * GOLD
    * WHITE
    * BLACK
    * RANDOM
      * sets the led to a randomly generated color
    * ROYGBIV
      * Easter Egg Command that sets the leds to a rainbow pattern

### Hardware

DDSat1 Hardware list:

* Raspberry Pi 4
* [Adafruit Servo Hat](https://www.adafruit.com/product/2327)
* 3x [Standard Size High Torque Servo](https://www.adafruit.com/product/1142)
* 2x [Circuit Playground Express](https://www.adafruit.com/product/3333)
* 2x [Solar to DC converter](https://www.adafruit.com/product/390)
* 2x [9W Solar Panel](https://www.adafruit.com/product/2747)

| Hardware Design |
| :---: |
| ![front](./photos/ddsatFront.jpg) |
| ![back](./photos/ddsatBack.jpg) |
| ![top](./photos/IMG_20200811_100851.jpg) |

## Things that didn't work

In the original design, the solar panels would actually power the two cpx boards directly.  To do this, a large led array was installed on top of the satellite to provide enough light for the panels.  The goal was to make it so that by rotating the panels the user would be able to physically cut power to those systems, which would be a step needed to gain control of the camera.  However several problems arouse from this set up.  

First, the lights that powered the solar panel were so bright that they washed out the colors on the cpx leds when filmed with the web cams.  This meant that the user couldn't tell the difference from one color command vs another.  

Additionally the light made it difficult to work in the room.  Besides being so bright, it also produced a lot of heat.  The university decided to cut the AC to our lab right before defcon, which meant it got well over 110F in the room with the satellite when the led array was on.  Attempts to provide cooling via external fans were not enough to keep all the systems running as well or stable as they needed to be.
