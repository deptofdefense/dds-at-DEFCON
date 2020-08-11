# CPX Simple Sat

Created as a part of the [Aerospace Village](https://aerospacevillage.org/) for DEFCON28 (Rest in Safe Mode), CPX Simple Sat attempts to teach the basics of satellite exploitation with a ground station in an easily approachable and jargon free manner.

## Background

Satellite hacking is one of those fields where all the best stories are kept behind closed doors.  Like the rest of Aerospace, the field suffers from a large amount of jargon that can make it difficult for the casual passerby to understand and follow.  Add to that the lack of thorough public documentation when events do happen, and it's easy to see why there are problems.  

In CPX Simple Sat we attempt to teach you some of the basic dangers and risks of satellite exploitation by creating an abstract version of a real world event.  In 2008, hackers used a ground station to communicate to and attempt to gain access to the Terra satellite (launched in 1999).  In the real world this is where the story ends, the hackers attempted to communicate with the satellite but didn't issue any commands, and the satellite itself was fine and is still working today.  But while the real life event may not have been that exciting, the concept this event represents poses an interesting challenge.

## The Game

In CPX Simple Sat, you the player have come into possession of a SpaceDotCom ground station, giving you the perfect chance to attack SpaceDotCom's CPX Simple Sat.  Why do you want to attack this random satellite you ask?  Maybe you got tired of all of Otter MiSpace's random otter facts (Did you know there are 13 species of Otters?), maybe he hired you to do this, or maybe you figured what else would you do when you wake up with a ground station in your home.  We just make the game, you can RP it however you like.  No one is here to judge.

Either way, you will be using a [Circuit Playground Express](https://www.adafruit.com/product/3333) (CPX) and [Raspberry Pi](https://www.raspberrypi.org/) that acts as the ground station you now control.  Due to COVID-19, you will be interacting with your ground station through a twitch chat bot.  To send a command to the chatbot, the message must start with "!", and all parameters are separated with a space.  For example, to log into the system, the twitch user would type "!cmd login `username` `password`".  Because there will be multiple people playing the game at once, we implemented a simple user management system by requiring users to type "!join" to get added to the user list and start playing the game.  Once on the list, each user will get one minute to complete their turn before it moves on to the next user in the list.  Your individual progress is saved and kept isolated from other users, so don't worry that you can't finish the game in one round.  

The satellite you will be interacting with is made out of a  [Circuit Playground Express](https://www.adafruit.com/product/3333) and [CRICKIT](https://www.adafruit.com/product/3093).  It talks to the ground station via the Inferred receiver and transmitter on each CPX board.  Due to this, sometimes a message may not be decoded properly.  If you think the state of the satellite is incorrect, then type "!reset" on your turn to resync it to your current state in the game.  

Using the game ICD, your goal in the game is to gain as much control of the satellite as you can by outwitting both its onboard systems and the remote ground station controlling it.  

### Game Documents

- [Game ICD](./SimpleSat_ICD.pdf)
- [Bonus Notes](./BONUS-cpx-sat-notes.pdf)

## DIY

If you want to create your own version of CPX Simple Sat, the STL files, build instructions, and source code can be found here: 

- [STL files and Assembly instructions](./3D_Files/README.md)
- [Build Guide](./buildGuide.md)
- Source code to be added after defcon
