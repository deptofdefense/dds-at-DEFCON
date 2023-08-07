# Python script to control a helper bot that will generate example traffic on the twitch channel

import time # needed to keep track of time between posts
import random # needed to randomize messages
from threading import Thread # needed for multithreading
from twitchio.ext import commands # needed for twitchIO chatbot
import yaml # needed for config
import asyncio # needed for async thread

class OtterBot(commands.Bot):
    """
    A Class to handle generating custom chat messages
    """

    def __init__(self, accessToken, prefix, channelList):
        """
        Initialization method
        """
        self.lastTransmissionTime = time.time()
        self.randomChatterThread = Thread(target=asyncio.run, args=(self.randomTransmission(),), daemon=True)
        self.randomChatterThread.start()

        super().__init__(token=accessToken, prefix=prefix, initial_channels=channelList)

    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        await self.connected_channels[0].send('OtterBot connected and ready to transmit!')

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:

            # Even if its us, reset the time for last transmission
            self.lastTransmissionTime = time.time()
            return

        # Print the contents of our message to console...
        # print(message.content)

        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)

    # Move command, used to tell the rover where to go
    @commands.command()
    async def move(self, ctx: commands.Context):
        # Since someone is talking to the rover, reset the time before we start sending messages
        self.lastTransmissionTime = time.time()

    # Camera command, used to pan the camera
    @commands.command()
    async def look(self, ctx: commands.Context):
        # Since someone is talking to the rover, reset the time before we start sending messages
        self.lastTransmissionTime = time.time()

    async def randomTransmission(self):

        while True:
            #print(str(time.time() - self.lastTransmissionTime))

            if (time.time() - self.lastTransmissionTime) >= 60:
                randMsg = self.generateMessage()
                await self.connected_channels[0].send(f'{randMsg}')
                print(randMsg)
                self.lastTransmissionTime = time.time()
                time.sleep(1)

            

    def generateMessage(self):

        commandType = random.randint(0, 100) # choice between movement and camera command

        if commandType <= 90: # do a movement command
            
            msg = "!move " # beginning of a move command

            messageLength = random.randint(1, 4) # how many commands are within the message

            for i in range(messageLength): 
                
                movementType = random.randint(1,100) 

                if movementType <= 25: # Go Forward
                    moveTime = random.randint(5, 15)
                    msg = msg + f"Go Forward for {str(moveTime)} seconds.  "
                
                elif movementType <= 50: # Turn Left
                    angle = random.randint(0, 180)
                    direction = random.randint(0, 1)
                    moveTime = random.randint(5, 15)

                    if direction == 0:
                        msg = msg + f"Turn Left {str(angle)} degrees and move forward {str(moveTime)} seconds.  "
                    else:
                        msg = msg + f"Turn Left {str(angle)} degrees and move in reverse {str(moveTime)} seconds.  "

                elif movementType <= 75: # Turn Right
                    angle = random.randint(0, 180)
                    direction = random.randint(0, 1)
                    moveTime = random.randint(5, 15)

                    if direction == 0:
                        msg = msg + f"Turn Right {str(angle)} degrees and move forward {str(moveTime)} seconds.  "
                    else:
                        msg = msg + f"Turn Right {str(angle)} degrees and move in reverse {str(moveTime)} seconds.  "

                else: # Reverse
                    moveTime = random.randint(5, 15)
                    msg = msg + f"Reverse and travel for {str(moveTime)} seconds.  "

        
        else: # do a camera command
            msg = "!look " # beginning of a look command

            cameraChoice = random.randint(0, 100)

            if cameraChoice <= 80: # set angle
                cameraAngle = random.randint(0, 180)
                msg = msg + f"Set camera angle to {str(cameraAngle)}"
            else:
                cameraAngle = random.randint(0, 180)
                cameraDirection = ""
                if random.randint(0,1) == 0: # set the adjustment to be to the right of the current angle
                    cameraDirection = "right"
                else:
                    cameraDirection = "left"
                msg = msg + f"Adjust camera angle by {str(cameraAngle)} to the {cameraDirection}"
        
        return msg
    

if __name__ == "__main__":

    print("Starting OtterBot")

    CFG = None  # global CFG settings
    with open("./configs/config.yml", "r") as ymlfile:
        CFG = yaml.safe_load(ymlfile)

    twitch_initial_channels = CFG["twitch"]["CHANNEL"]
    twitch_prefix = CFG["twitch"]["BOT_PREFIX"]
    twitch_access_token = CFG["twitch"]["OTTER_ACCESS_TOKEN"]

    otter = OtterBot(twitch_access_token, twitch_prefix, twitch_initial_channels)
    otter.run()

