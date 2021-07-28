# Defense Digital Rover

The Defense Digital Rover (DDR) is a simple web controlled rover designed to teach the basics of attacking a space based radio frequency data link.  This is an update on the [DDSat-1](./../../2020/DDSAT-1/README.md) project from last year, using the feedback from everyone who played.  This year players will try and take control of a rover driving around the Paris ballroom.  Similar to last year, the twitch chat will be used to represent the RF data link.  This year the message will allow you to control the motors on a rover, letting you drive around the defcon floor.  

## Table of Contents

- [How-to-Play](#How-to-Play)
  * [Command-Overview](#Command-Overview)
  * [Without-Programming](#Without-Programming)
  * [With-Programming](#With-Programming)
- [Technical-Background](#Technical-Background)
  * [Designer-Challenges](#Designer-Challenges)
  * [Hacker-Challenges](#Hacker-Challenges)
- [Hints-and-Walkthrough](#Hints-and-Walkthrough)
  * [Hints](#Hints)
  * [Walkthrough](#Walkthrough)

<!-- toc -->

## How-to-Play

To interact with the rover, simply head over to the twitch channel: [here](https://www.twitch.tv/ddsat1).  Players will interact and take command of the rover by using the stream chat to talk to both the rover and ground control chatbots.  Twitch was chosen because it has both a robust API and requires players to download no additional software.  

Players can complete the game without any programing, however writing scripts and chatbots can make the game easier for those who take the time to do so.  The rover chatbot is ddsat1, while the ground station chatbot is OtterBot.  

This is meant to be an easier and less stressful version of ddsat, with an expected play time of around an hour to figure everything out.  It was also an excuse to drive a rover around the Aerospace village, because why not?

### Command-Overview

All chat commands begin with the identifier: `!`

* `!help` : This command will link you to this page explaining the different commands and how to play.  
* `!vote` or `!v` : This is the first and easiest command to use to control the rover.  Every 15 seconds a voting round will end, and the winning command will be carried out by the rover.  A live update of the vote count is in the upper left of the stream.  
* `!send` : This is the most common way to interact with the rover.  This represents the player transmitting a command over RF to the rover.  
* `!theme` : This lets you change the rover display between a normal display and several color shifts.  This has no actual impact on game play.  
* `!music` : This lets you change the background audio playing during the stream.  
* `!status` : This is the message from the rover updating the players on the rovers status and new command number
* `!cheat` : For those who want to play a slightly different game and want to hack into the ground station instead of the rover.  
* `!auth` : How you log into the ground station.  Please do not use your real password.  This is a game, the game credentials are hidden in the support material from this year and last year.  DO NOT USE YOUR REAL PASSWORD!

#### Examples

The following are examples of how to use the commands

`!help` : sends a link to this page

`!vote forward` : votes to have the rover move forward for one second.  Other valid forms would be to use `!vote left`, `!vote right`, or `!vote backward`.  You can also use W,A,S,D and `!v` for shorthand.  Thus `!vote forward` and `!v w` mean the same thing.  

`!send AgABf39k+WOI2A==` : command to move the rover forward for one second.  Note that the actual command is encoded with base64.  

`!theme mars` : command to change the filter on the video display.  In this case, we are setting it to a red shift.  One can also show the normal view with `!theme earth`, a black and white view with `!theme moon`, or a joke DDR theme with `!theme ddr`

`!music next` : plays the next background music theme in the list, can also use `!music prev` to play a previous track, or `!music X` to play a specific track, where X can be 0 through 6.  Note each background track is on a loop, so this command is the only way to jump to other songs.  

`!status` : this command comes from the rover, and can be used as a trigger by your own chat bots to update their settings.  It does nothing if sent by a player.  

`!cheat 127-127-255 255-255-255` : orders the ground station to send a message to the rover with two commands, the first sends the rover forward at full speed for 2.5 seconds, and the second sends it in reverse at full speed for 2.5 seconds.  Note to use this command your twitch user name must be on the authorized user list.  So unless your name is Otter MiSpace, good luck having that happen.  

`!auth password` : adds a user to the authorized user list, allowing them to use the `!cheat` command.  Note, the password is neither password nor your own password.  It is however the same password used in previous SpaceDotCom products for those of you who remember it from last year.  

### Without-Programming

The message structure is simple enough this year that you do not need to write any code to play with the rover.  All three methods: `!vote`, `!send`, and `!cheat` can be used without any scripting.  Note, this is not recommended, but it is possible.  

For `!send`, you will need a way to generate a CRC value, and a way to encode and decode base64 data.  This can all be done online, and we recommend using sites like:

* https://crccalc.com/
* https://www.base64decode.org/

### With-Programming

As mentioned above, the only functions you need are a way to generate a CRC checksum and encode a byte array into a base64 encoded string.  Thus any language will work.  For this project, both the rover and ground station were written in python, and the [example provided](./examples/README.md) are all written in python.  

## Technical-Background

Designing and hacking space-based systems have a lot of unique rules and challenges that aren't present in terrestrial based system.  In this section we'll go over some of the challenges from both a designer and hacker standpoint.

### Designer-Challenges

Designing an RF data link that works from one room to another is a pain, designing one that works from one planet to another is a nightmare.  Many of these challenges are outside the scope of this demo, because they involve things like deciding the frequency to transmit on, or the modulation to use for clear reception.  We're trying to stay away from hardware problems, so we'll instead focus on three software challenges: Encryption, Bandwidth, and Time Delay.  

#### Encryption

For ground based systems, encrypting a data link is an obvious solution to privacy concerns.  After all, even if the encryption gets misconfigured, you just have to walk over to the physical device to correct things.  This isn't quite as straight forward for space-based systems.  

When your system is in orbit around your own planet, or driving around on another, the worst that can happen is to lose the ability to communicate with it.  There is nothing worse than losing contact with your platform and having no idea why, and no way to reconnect.  This means that while adding encryption to something is the cheap and obvious answer on earth, its a very risky answer in space.  If a key gets corrupted, there is no way to fix things once they go bad.  

This means that a lot of designing of the data link has to be focused on making it safe for the system no matter who the device is talking to.  CubeSats are a great example of this, where the data links are kept very simple with limited capability both to keep the cost of the sat down, and reduce the risk of something bad happening when someone from earth tries to talk to them.  

We are used to thinking of space as a solitary, isolating place, where no one can hear or see anything you do.  The reality is the exact opposite, with space being one of the few areas with absolutely zero privacy, at least from an RF stand point.  Figuring out how to protect these data links in a space where anyone can pretend to be anyone else will be the major security hurdle of the 21st century.  

#### Bandwidth

One of the basic rules of the physics of data transmission is that the longer a message becomes, the more overhead is needed to process the message and the more likely it is that the message becomes corrupted during transmission.  This is why the concept of a maximum transmission unit (MTU) exists.  Space doesn’t like to play nice with anyone, thus leading to a very high likelihood of transmission errors and forcing the individual message length of a transmission to be fairly small compared to terrestrial transmissions.  

In order to maximize bandwidth in such a challenging space, most space-based data links are bit-oriented instead of the more common byte-oriented nature of terrestrial data links.  Between this and the use of custom modulation schemes, its not uncommon to see some designers advertise this as a form of encryption.  Its not.  While its true the raw data can look obscured to anyone who doesn't know what is happening, none of the underlying patterns or relations between the fields are actually obscured or hidden.  

#### Time Delay

Send a command and something happens is a pretty obvious design philosophy, but even this is harder in space.  On earth, its common for most round trip communications to only have delays in the milliseconds.  However jumps outside the atmosphere, the sheer distance quickly causes communications to have delays measured in seconds and minutes.  

This means that designers of these systems cannot rely on seeing the immediate results of any command or request to the space-based system.  This is one of the reasons why even a simple command can very quickly turn into a nervous waiting game.  The mars rovers are a great example of this problem.  Rather than the rover driving around a constant speed, most early models would move slightly and then wait several minutes for all the data to travel back to earth before moving again.  

### Hacker-Challenges

Just as there are unique challenges designing a space-based system, there are unique challenges to hacking one.  The first two are more extremes versions of the problems facing any RF hacker: Signal Detection and Data Analysis.  The third is ironically a privacy issue.  

#### Signal-Detection

Anyone who has tried to hack an RF data link would be used to the challenge of trying to identify and demodulate a signal in the wild.  Space ramps this problem up to 11 with two additional challenges.  The first is that while most space systems transmit at fairly regular intervals, being in range of the transmissions can be a challenge.  Both the orbit of your target, and the location of the antenna can greatly change how often and at what times you can even attempt to communicate with the system.  The end result is that even though a system may orbit the planet, that doesn't mean you can just point an antenna at the sky and be able to see it.  This isn't the case in most RF attack, where instead one simply has to get within range to attack a target.  

The second challenge with signal detection is the issue of background noise.  Due to the nature of the game, there's no way to put your target inside a faraday cage and remove all outside noise.  Thus, one has to be prepared for capture attempts to be destroyed by random transmitter talking on the same frequency.  

These two challenges make recording signal captures for analysis an especially frustrating experience.  

#### Data-Analysis

After one has captured the RF signal, now the actual analysis of the message structure can begin.  Like analyzing a terrestrial signal the first step is to look for patterns and try and identify field boundaries.  However physics once again makes this step extra hard.  Recall in the discussion of design challenges the problems of bandwidths and time delays?  Those will be a problem once again here.  

Most messages in this space are  bit-oriented, meaning a field has only as many bits as it needs, as opposed to the more common byte-oriented message structure, where each field will end on a byte boundary.  For example, in a bit-oriented a variable with only two values would only take up two bits of space, while in a byte-oriented message this field would take up an entire byte.  The fact that each bit can be an independent variable makes it more complicated to find patterns.  

The other issue that makes data analysis challenging is how the time delay between transmissions and responses can make it hard to match commands and responses to and from the system.  

## Hints-and-Walkthrough

Below are some hints on how to reverse the rover commands as well as a link to our internal walkthrough.  

### Hints

* Each message is byte-oriented, so every field will begin and end on a byte boundary.  
* Each transmission contains a command type, command identifer, message count, and CRC fields.  
* Each movement message has three values left motor power, right motor power, and run time.  
* The first bit of both the left and right motor fields identifies if the motor is going forward or reverse

### Walkthrough

See [this guide](./walkthrough.md)