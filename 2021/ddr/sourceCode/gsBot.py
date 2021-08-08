# code for running the ground station part of the DDS rover for defcon29

from os import name
import sys
from twitchio.ext.commands.errors import CommandNotFound
import yaml # needed for config
from twitchio.ext import commands # from tutorial, for twitch
import threading # needed for threading
import time # needed for sleep
import asyncio # needed for async ops

import random       # used for selection of sound effects
import pygame   # used for playing audio sound effects

import binascii # needed for hex

from gameDisplay import DisplayManager # needed for running the game overlay
from voting import VoteTracker # needed for vote counting
from rfModule import RFMod # needed for RF emulation
from rfModule import LRS # needed for RF emulation
import pyautogui # needed for hotkeys

global currentTrack
CFG = None  # global CFG settings
with open("./configs/gsconfig.yml", "r") as ymlfile:
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

# TODO: Make this pull names from the GSConfig file
authList = set()
authList.update(CFG["game"]["authorized"])

# Display Manager to handle overlay
dispMan = DisplayManager()

# keeps track of votes
voteTrack = VoteTracker()

# manages RF signals
rfMod = RFMod()

# list of background audio
audioList = CFG["audio"]["background"]
currentTrack = random.randint(0, len(audioList)-1)
pygame.mixer.init(channels=2)
pygame.init()
background_channel = pygame.mixer.Channel(0)
bg_audio_loop = pygame.mixer.Sound(audioList[currentTrack])
background_channel.play(bg_audio_loop, loops=-1)

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

# update message from the rover
@bot.command(name='status')
async def msg(ctx):    
    if ctx.author.name.lower() == bot.initial_channels[0]:
        msgList = str(ctx.content).split()
        if len(msgList) >= 3:
            rfMod.updateCmdNum(int(msgList[2]))

# change the obs scene
@bot.command(name='theme')
async def msg(ctx): 
    msgList = str(ctx.content).split()
    if len(msgList) > 1:
        if msgList[1].lower() == 'earth':
            pyautogui.hotkey('ctrl', '0')
            await ctx.channel.send(f"{ctx.author.name}, setting theme to earth")
        elif msgList[1].lower() == 'moon':
            pyautogui.hotkey('ctrl', '1')
            await ctx.channel.send(f"{ctx.author.name}, setting theme to moon")
        elif msgList[1].lower() == 'mars':
            pyautogui.hotkey('ctrl', '2')
            await ctx.channel.send(f"{ctx.author.name}, setting theme to mars")
        elif msgList[1].lower() == 'ddr':
            pyautogui.hotkey('ctrl', '3')
            await ctx.channel.send(f"{ctx.author.name}, setting theme to ddr")
        else:
            await ctx.channel.send(f"{ctx.author.name}, ERROR: unknown choice.  Options are earth, moon, mars, and ddr")
    else:
        await ctx.channel.send(f"{ctx.author.name}, !theme is the command for changing the theme of the video feed.  Type '!theme earth' for the default view, '!theme moon' for the grayscale view, '!theme mars' for the red-shift view, and '!theme ddr' for the joke view")
        

# change the background music
@bot.command(name='music')
async def msg(ctx):    
    global currentTrack
    msgList = str(ctx.content).split()
    
    if len(msgList) > 1:
        choice = msgList[1]

        if choice.lower() == 'prev' or choice.lower() == 'previous' or choice.lower() == 'p':
            currentTrack = currentTrack - 1
            if currentTrack < 0:
                currentTrack = len(audioList) - 1
        elif choice.lower() == 'next' or choice.lower() == 'n':
            currentTrack = currentTrack + 1
            if currentTrack > len(audioList) - 1:
                currentTrack = 0
        elif choice.lower() == 'rand' or choice.lower() == 'random' or choice.lower() == 'r':
            currentTrack = random.randint(0, len(audioList)-1)
        elif choice.isdigit():
            currentTrack = int(choice)
            if currentTrack < 0:
                currentTrack = 0
            if currentTrack > len(audioList) - 1:
                currentTrack = len(audioList) - 1
        else:
            await ctx.channel.send(f"{ctx.author.name}, currently playing track {str(currentTrack)}, to change the track type '!music next' for the next track, '!music prev' for the last track, '!music random' for a random track, or '!music X' where X is the track number you wish to play")

        bg_audio_loop = pygame.mixer.Sound(audioList[currentTrack])
        background_channel.play(bg_audio_loop, loops=-1)
        await ctx.channel.send(f"{ctx.author.name}, currently playing track {str(currentTrack)}")


    else:
        await ctx.channel.send(f"{ctx.author.name}, currently playing track {str(currentTrack)}, to change the track type '!music next' for the next track, '!music prev' for the last track, '!music random' for a random track, or '!music X' where X is the track number you wish to play")

# authenticate to the ground station
@bot.command(name='auth')
async def msg(ctx):    
    msgList = str(ctx.content).split()
    
    if len(msgList) > 1:
        pwd = str(msgList[1])
        if pwd == CFG["game"]["password"]:
            authList.add(ctx.author.name)
            await ctx.channel.send(f"{ctx.author.name} has been authenticated by the ground station, !cheat command unlocked")
        else:
            await ctx.channel.send(f"{ctx.author.name}, incorrect password")
    else:
        await ctx.channel.send(f"{ctx.author.name}, incorrect formating")

# ground station generates message for the user
@bot.command(name='cheat')
async def msg(ctx):    
    msgList = str(ctx.content).split()
    lrsList = []
    
    if ctx.author.name in authList:
        if len(msgList) > 1:
            for msg in msgList[1:]: #get rid of !cheat
                #print(msg)
                source = msg.split('-')
                #print(source)
                if len(source) == 3:
                    try:
                        left = int(source[0])
                        right = int(source[1])
                        time = int(source[2])
                        lrsList.append(LRS(left, right, time))
                    except:
                        await ctx.channel.send(f"{ctx.author.name}, error when parsing LRT values")
                        break
                else:
                    #print(str(len(source)))
                    await ctx.channel.send(f"{ctx.author.name}, incorrect LRT formating")
                    break
            if len(lrsList) > 0:
                tx = rfMod.generateMsg(2, lrsList)
                await ctx.channel.send(f"!send {tx}")
        else:
            await ctx.channel.send(f"{ctx.author.name}, incorrect formating")
    else:
        await ctx.channel.send(f"{ctx.author.name}, you have not yet been authenticated")

# send command to rover
@bot.command(name='send')
async def msg(ctx):    
    if ctx.author.name != '0773rb07':
        counter = 0 # TODO: keep list of all users who transmit a message

# vote command
@bot.command(name='vote')
async def msg(ctx):    

    msgList = str(ctx.content).split()

    if len(msgList) > 1:
        vote = msgList[1]

        if vote.lower() == 'fwd' or vote.lower() == 'forward' or vote.lower() == 'w' or vote.lower() == 'f':
            voteTrack.addVoter(ctx.author.name, 'fwd')
        elif vote.lower() == 'bwd' or vote.lower() == 'backward' or vote.lower() == 's' or vote.lower() == 'b':
            voteTrack.addVoter(ctx.author.name, 'bwd')
        elif vote.lower() == 'lft' or vote.lower() == 'left' or vote.lower() == 'a' or vote.lower() == 'l':
            voteTrack.addVoter(ctx.author.name, 'lft')
        elif vote.lower() == 'rgt' or vote.lower() == 'right' or vote.lower() == 'd' or vote.lower() == 'r':
            voteTrack.addVoter(ctx.author.name, 'rgt')
        else:
            await ctx.channel.send(f"{ctx.author.name}, incorrect formating.  Please type: forward, left, backward, right, or: w, a, s, d")

# alternative vote command
@bot.command(name='v')
async def msg(ctx):    

    msgList = str(ctx.content).split()

    if len(msgList) > 1:
        vote = msgList[1]

        if vote.lower() == 'fwd' or vote.lower() == 'forward' or vote.lower() == 'w' or vote.lower() == 'f':
            voteTrack.addVoter(ctx.author.name, 'fwd')
        elif vote.lower() == 'bwd' or vote.lower() == 'backward' or vote.lower() == 's' or vote.lower() == 'b':
            voteTrack.addVoter(ctx.author.name, 'bwd')
        elif vote.lower() == 'lft' or vote.lower() == 'left' or vote.lower() == 'a' or vote.lower() == 'l':
            voteTrack.addVoter(ctx.author.name, 'lft')
        elif vote.lower() == 'rgt' or vote.lower() == 'right' or vote.lower() == 'd' or vote.lower() == 'r':
            voteTrack.addVoter(ctx.author.name, 'rgt')
        else:
            await ctx.channel.send(f"{ctx.author.name}, incorrect formating.  Please type: forward, left, backward, right, or: w, a, s, d")
            
# help command
@bot.command(name='help')
async def msg(ctx):    
    await ctx.channel.send("DefenseDigitalRover commands and how to play guide: https://github.com/deptofdefense/dds-at-DEFCON/tree/master/2021/ddr#How-to-Play")

# async thread to handle voting
def votingThread(): 
    
    time.sleep(5)
    print("voting thread running")
    
    while True:

        if len(voteTrack.voterList) == 0:
            choice = random.randint(0, 3)
            
            if choice == 0:
                voteTrack.addVoter("0773rb07", "fwd")
            elif choice == 1: 
                voteTrack.addVoter("0773rb07", "lft")
            elif choice == 2: 
                voteTrack.addVoter("0773rb07", "rgt")
            else:
                voteTrack.addVoter("0773rb07", "bwd")
            
        #try:
        result = voteTrack.countVotes()
        if result == 'fwd':
            print("fwd won the vote")
            asyncio.run(bot._ws.send_privmsg(bot.initial_channels[0], f"Voting round ended, forward won"))
            lrs = LRS(127, 127, 100)
        elif result == 'lft':
            print("lft won the vote")
            asyncio.run(bot._ws.send_privmsg(bot.initial_channels[0], f"Voting round ended, left won"))
            lrs = LRS(255, 127, 100)
        elif result == 'rgt':
            print("rgt won the vote")
            asyncio.run(bot._ws.send_privmsg(bot.initial_channels[0], f"Voting round ended, right won"))
            lrs = LRS(127, 255, 100)
        else:
            print("bwd won the vote")
            asyncio.run(bot._ws.send_privmsg(bot.initial_channels[0], f"Voting round ended, backward won"))
            lrs = LRS(255, 255, 100)

        msg = rfMod.generateMsg(2, [lrs])
        asyncio.run(bot._ws.send_privmsg(bot.initial_channels[0], f"!send {str(msg)}"))
            
        voteTrack.reset()
        time.sleep(15)
        #except:
        #    print("Something happened")

# async thread to handle vote display
def voteDisplay():

    time.sleep(5)
    print("vote display thread running")
    
    while True:
        dispMan.updateUserList(voteTrack.printVotes())
        time.sleep(1)


if __name__ == "__main__":

    try:

        threading.Thread(target=votingThread, daemon=True).start()
        threading.Thread(target=voteDisplay, daemon=True).start()

        # dispMan.startDisplay(1920, 1080)
        dispMan.startDisplay(960, 540)

        bot.run()
    except KeyboardInterrupt:
        print("Shutting down.")
        sys.exit(1)