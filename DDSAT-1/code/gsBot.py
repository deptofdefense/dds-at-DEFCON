# Code for managing the ground station part of DDSat1
# Created for defcon28 Aerospace Village

import yaml # needed for config
from twitchio.ext import commands # from tutorial, for twitch
import threading # needed for threading
import time # needed for sleep
import asyncio # needed for async ops

import random       # used for selection of sound effects
import pygame   # used for playing audio sound effects

import binascii # needed for hex

from groundSatation import GroundStation # needed for game

CFG = None  # global CFG settings
with open("gsconfig.yml", "r") as ymlfile:
    CFG = yaml.safe_load(ymlfile)

# pulling the values from config.yml
# keeping them separate for flexibilitycode sharing
bot = commands.Bot(
    irc_token = CFG["twitch"]["TMI_TOKEN"],
    client_id = CFG["twitch"]["CLIENT_ID"],
    nick = CFG["twitch"]["BOT_NICK"],
    prefix =CFG["twitch"]["BOT_PREFIX"],
    initial_channels = CFG["twitch"]["CHANNEL"]
)

gs = GroundStation(CFG)

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

# message command
@bot.command(name='rsp')
async def msg(ctx):

    msgList = str(ctx.content).split()

    if len(msgList) > 1:
        #response = ddsat1.processCmd(msgList[1])
        temp = str(msgList[1])

        valid, cmd, stat = gs.decodeMsg(temp)
        
        if valid:
            gs.updateCmdNum((int(cmd)+1))
            resp = binascii.a2b_hex(stat).decode()

            print(resp)
    else: 
        print("nope")
        #response = "Error, incorrect use of !msg"

    #await ctx.channel.send(f"{ctx.author.name}: {response}")

# message command
@bot.command(name='status')
async def msg(ctx):

    msgList = str(ctx.content).split()

    if len(msgList) > 1:
        #response = ddsat1.processCmd(msgList[1])
        #print("got a response")
        #print (msgList[1])

        temp = str(msgList[1])

        valid, cmd, stat = gs.decodeMsg(temp)
        
        if valid:
            gs.updateCmdNum((int(cmd)+1))
            statusMsg = binascii.a2b_hex(stat).decode()

            print(statusMsg)
    else: 
        print("nope")
        #response = "Error, incorrect use of !msg"

    #await ctx.channel.send(f"{ctx.author.name}: {response}")

@bot.command(name='send')
async def msg(ctx):

    msgList = str(ctx.content).split()
    
    if ctx.author.name == 'zeetwii':
        if len(msgList) > 1:
            cmdMsg = gs.generateCmdMsg(msgList[1])

            await ctx.channel.send(f"!msg {cmdMsg}")


        else: 
            print("nope")
            #response = "Error, incorrect use of !msg"

        #await ctx.channel.send(f"{ctx.author.name}: {response}")
    else:
        await ctx.channel.send(f"{ctx.author.name}: you are not a ground station user.  try reversing the satellite commands")


def randCmdThread():

    print("command thread running")

    colorList = ["RED", "ORANGE", "YELLOW", "GREEN", "CYAN", "BLUE", "INDIGO", "VIOLET", "PURPLE", "GOLD", "WHITE", "BLACK", "RANDOM"]

    while True:
        time.sleep(15)

        choice = random.randint(0,2)
        cmdMsg = ''

        if choice == 0: # payload
            choice = random.randint(0,1) # again for payload

            if choice == 0: # Payload 1
                target = "PAY01"
                choice = random.randint(0,9) # again for affect
                if choice == 0 : # Lite
                    cmdMsg = gs.generateCmdMsg(f"{target}L")
                elif choice == 1: # Temp
                    cmdMsg = gs.generateCmdMsg(f"{target}T")
                else: # Color
                    color = colorList[random.randint(0, (len(colorList) - 1))]
                    choice = random.randint(0,2) # again for placing
                    if choice == 0: # All
                        cmdMsg = gs.generateCmdMsg(f"{target}A{color}")
                    elif choice == 1: # Top
                        cmdMsg = gs.generateCmdMsg(f"{target}U{color}")
                    else: # bottom
                        cmdMsg = gs.generateCmdMsg(f"{target}U{color}")
                
            else:
                target = "PAY02"
                choice = random.randint(0,9) # again for affect
                if choice == 0 : # Lite
                    cmdMsg = gs.generateCmdMsg(f"{target}L")
                elif choice == 1 : # Temp
                    cmdMsg = gs.generateCmdMsg(f"{target}T")
                else : # Color
                    color = colorList[random.randint(0, (len(colorList) - 1))]
                    choice = random.randint(0,2) # again for placing
                    if choice == 0: # All
                        cmdMsg = gs.generateCmdMsg(f"{target}A{color}")
                    elif choice == 1: # Top
                        cmdMsg = gs.generateCmdMsg(f"{target}U{color}")
                    else: # bottom
                        cmdMsg = gs.generateCmdMsg(f"{target}U{color}")
                
        elif choice == 1: # battery
            choice = random.randint(0,1) # which battery
            if choice == 0: # bat01
                target = "BAT01"
                angle = str(random.randint(0,180))
                cmdMsg = gs.generateCmdMsg(f"{target}A{angle}")
            else:
                target = "BAT02"
                angle = str(random.randint(0,180))
                cmdMsg = gs.generateCmdMsg(f"{target}A{angle}")
        else: # camera
            angle = str(random.randint(0,180))
            cmdMsg = gs.generateCmdMsg(f"CAM01A{angle}")

        asyncio.run(bot._ws.send_privmsg(bot.initial_channels[0], f"!msg {cmdMsg}"))

if __name__ == "__main__":

    threading.Thread(target=randCmdThread, daemon=True).start()

    bot.run()