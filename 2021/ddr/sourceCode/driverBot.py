# code for running the ground station part of the DDS rover for defcon29

import yaml # needed for config
from twitchio.ext import commands # from tutorial, for twitch
import threading # needed for threading
import time # needed for sleep
import asyncio # needed for async ops

import random       # used for selection of sound effects
import pygame   # used for playing audio sound effects

import binascii # needed for hex

from rover import Rover # needed to drive the rover
from rfModule import RFMod # needed for RF emulation
from rfModule import LRS # needed for RF emulation

CFG = None  # global CFG settings
with open("./configs/config.yml", "r") as ymlfile:
    CFG = yaml.safe_load(ymlfile)

# pulling the values from config.yml
# keeping them separate for flexibility code sharing
bot = commands.Bot(
    irc_token = CFG["twitch"]["TMI_TOKEN"],
    client_id = CFG["twitch"]["CLIENT_ID"],
    nick = CFG["twitch"]["BOT_NICK"],
    prefix =CFG["twitch"]["BOT_PREFIX"],
    initial_channels = CFG["twitch"]["CHANNEL"]
)

# rover instance
ddRov = Rover()
rfMod = RFMod()

# bot connection event
@bot.event
async def event_ready():
    global CFG

    print(CFG["twitch"]["BOT_NICK"] + " is online!")
    ws = bot._ws
    await ws.send_privmsg(bot.initial_channels[0], f"/me is now operational")

# event for user entering something in chat
@bot.event
async def event_message(ctx):
    global CFG

    if ctx.author.name.lower() == CFG["twitch"]["BOT_NICK"].lower():
        return
    await bot.handle_commands(ctx)
    #print(f'{ctx.channel} - {ctx.author.name}: {ctx.content}')

# send command to rover
@bot.command(name='send')
async def msg(ctx):    
    
    msgList = str(ctx.content).split()
    
    if len(msgList) > 1:
        
        valid, response, lrtList = rfMod.decodeMsg(msgList[1])

        await ctx.channel.send(f"{ctx.author.name}: {response}")

        if valid:
            if not ddRov.isBusy():
                ddRov.drive(lrtList)
            else:
                await ctx.channel.send(f"Rover is busy, skiping command")
                time.sleep(0.01)

            #for lrt in lrtList:
                #print(lrt.getASCIITuple())
        
        await ctx.channel.send(f"!status newCN: {str(rfMod.cmdNum)}")
        
if __name__ == "__main__":
    
    threading.Thread(target=ddRov.lineDetectThread, daemon=True).start()
    bot.run()