import sys
from twitchio.ext import commands
import yaml # needed for config
import threading # needed for threading
import time # needed for sleep
import random       # used for selection of sound effects
import pygame   # used for playing audio sound effects

import binascii # needed for hex

from gameDisplay import DisplayManager # needed for running the game overlay
from voting import VoteTracker # needed for vote counting
from rfModule import RFMod # needed for RF emulation
from rfModule import LRS # needed for RF emulation
import pyautogui # needed for hotkeys
import asyncio # needed for async ops


class Bot(commands.Bot):

    def __init__(self, configFile):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...

        with open(configFile, "r") as ymlfile:
            cfg = yaml.safe_load(ymlfile)

            # twitch variables
            accessToken = cfg['bot']['accessToken']
            prefix = cfg['bot']['prefix']
            initChannels = cfg['bot']['channels']

            # game variables
            self.adminName = cfg['game']['username']
            self.password = cfg['game']['password']

            # authorized user list
            authList = set()
            authList.update(cfg['game']['authorized'])

            # Display Manager to handle overlay
            self.dispMan = DisplayManager()

            # keeps track of votes
            self.voteTrack = VoteTracker()

            # manages RF signals
            self.rfMod = RFMod()

            # list of background audio
            self.audioList = cfg['audio']['background']
            self.currentTrack = random.randint(0, len(self.audioList)-1)
            pygame.mixer.init(channels=2)
            pygame.init()
            self.background_channel = pygame.mixer.Channel(0)
            self.bg_audio_loop = pygame.mixer.Sound(self.audioList[self.currentTrack])
            self.background_channel.play(self.bg_audio_loop, loops=-1)

        super().__init__(token=accessToken, prefix=prefix, initial_channels=initChannels)


    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return

        # Print the contents of our message to console...
        print(message.content)

        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)

    @commands.command()
    async def hello(self, ctx: commands.Context):
        # Here we have a command hello, we can invoke our command with our prefix and command name
        # e.g ?hello
        # We can also give our commands aliases (different names) to invoke with.

        # Send a hello back!
        # Sending a reply back to the channel is easy... Below is an example.
        await ctx.send(f'Hello {ctx.author.name}!')

    def testThread(self):

        time.sleep(6)
        
        chan = self.get_channel("defensedigitalrover")

        while True:
            asyncio.run(chan.send("test message"))
            time.sleep(5)



bot = Bot("./configs/gsconfig.yml")

threading.Thread(target=bot.testThread, daemon=True).start()

bot.run()
# bot.run() is blocking and will stop execution of any below code here until stopped or closed.