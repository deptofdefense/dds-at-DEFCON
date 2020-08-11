# aerobot.py
# Created for defcon28 aerospace village

import yaml # needed for config
from simpleSat import SimpleSat # needed to manage game

from twitchio.ext import commands # from tutorial, for twitch

from userList import UserList # needed for user management
from userList import SatUser # needed for user management

import threading # needed for threading
import time # needed for sleep
import asyncio # needed for async ops

import binascii # needed for serial
import serial # needed for serial
import struct # needed for serial

from gameDisplay import DisplayManager # needed for running the game overlay

CFG = None  # global CFG settings
with open("config.yml", "r") as ymlfile:
    CFG = yaml.safe_load(ymlfile)

# manages the game
simpleSatGame = SimpleSat(CFG)

# user list for managing active connections
userList = UserList()

# Display Manager to handle overlay
dispMan = DisplayManager()

# pulling the values from config.yml
# keeping them separate for flexibilitycode sharing
bot = commands.Bot(
    irc_token = CFG["twitch"]["TMI_TOKEN"],
    client_id = CFG["twitch"]["CLIENT_ID"],
    nick = CFG["twitch"]["BOT_NICK"],
    prefix =CFG["twitch"]["BOT_PREFIX"],
    initial_channels = CFG["twitch"]["CHANNEL"]
)

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
    print(f'{ctx.channel} - {ctx.author.name}: {ctx.content}')

# reset command - proof of concept
@bot.command(name='reset')
async def reset(ctx):

    if userList.getCurrentUser().matchName(ctx.author.name):

        userList.getCurrentUser().resetTimeout()

        simpleSatGame.reset(userList.getCurrentUser().getCurrentStep())

        await ctx.channel.send(f"{ctx.author.name} sent the command reset")

    else:
        await ctx.channel.send(f"{ctx.author.name}, it is not your turn to use the ground station")

# replay command - sets the current step to 0 so the user may replay the game
@bot.command(name='replay')
async def replay(ctx):
    if userList.getCurrentUser().matchName(ctx.author.name):

        userList.getCurrentUser().resetTimeout()

        userList.getCurrentUser().setCurrentStep(0)

        simpleSatGame.reset(userList.getCurrentUser().getCurrentStep())

        await ctx.channel.send(f"{ctx.author.name} sent the replay command")

    else:
        await ctx.channel.send(f"{ctx.author.name}, it is not your turn to use the ground station")

# generic command - meant to be flexible
@bot.command(name='cmd')
async def cmd(ctx):

    if userList.getCurrentUser().matchName(ctx.author.name):

        userList.getCurrentUser().resetTimeout()

        msg = simpleSatGame.checkCmd(userList.getCurrentUser(), ctx.content)

        dispMan.updateCmdMsg(ctx.content)

        await ctx.channel.send(f"{ctx.author.name}: {msg}")

    else:
        await ctx.channel.send(f"{ctx.author.name}, it is not your turn to use the ground station")

# theme command - allows the user to change background music
@bot.command(name='theme')
async def theme(ctx):

    msg = simpleSatGame.setTheme(SatUser(ctx.author.name), ctx.content)
    await ctx.channel.send(f"{ctx.author.name}: {msg}")

# join command - allows user to join the user list
@bot.command(name='join')
async def join(ctx):
    if userList.addUser(ctx.author.name):
        if len(userList.getUserList()) == 1:
            await ctx.channel.send(f"{ctx.author.name} has joined the user list for this control station, and is now the active user")
        else:
            await ctx.channel.send(f"{ctx.author.name} has joined the user list for this control station")
    else:
        await ctx.channel.send(f"{ctx.author.name}, you are already on the user list")

# leave command - allows user to leave the user list before they timeout
@bot.command(name='leave')
async def leave(ctx):
    if userList.removeUser(ctx.author.name):
        await ctx.channel.send(f"{ctx.author.name} has left the user list for this control station")
        dispMan.updateUserList(userList.getNextUserList(5))

        # reset current user if they left
        if userList.getCurrentUser().matchName(ctx.author.name):
            userList.setCurrentUser(SatUser("temp"))

    else:
        await ctx.channel.send(f"{ctx.author.name}, you are not on the user list")

# help command - link to repo readme with instructions
@bot.command(name='help')
async def help(ctx):
    global CFG

    helpList = ctx.content.split()

    if len(helpList) == 1:
        await ctx.channel.send(f'Hello {ctx.author.name}: The main commands for the game are on the right side of your screen, just type them in chat.  If you don\'t understand a command, type "!help <command>" for more info.  to get the background story or game ICD, go to: https://github.com/deptofdefense/dds-at-DEFCON/tree/master/CPX-simplesat . Retweet @DefenseDigital for free swag on our last day')
    else:
        if helpList[1].lower() == "join" or helpList[1].lower() == "!join":
            await ctx.channel.send(f'"!join" is the command used to join the user list for taking control of the game.  Each turn lasts 1 min and the game rotates between users in the userlist in a round robin fashion.  You can see the next 5 users in the left hand corner of your screen')
        elif helpList[1].lower() == "leave" or helpList[1].lower() == "!leave":
            await ctx.channel.send(f'"!leave" is the command used to leave the user list early.  A user will also leave the list if they timeout and send no commands for 3 turns')
        elif helpList[1].lower() == "reset" or helpList[1].lower() == "!reset":
            await ctx.channel.send(f'"!reset" is the command used to reset the state of the satellite.  Because the satellite is talking over IR to the ground station it will sometimes miss commands.  To fix this, use !reset to resync the satellite and ground station')
        elif helpList[1].lower() == "replay" or helpList[1].lower() == "!replay":
            await ctx.channel.send(f'"!replay" is the command used to reset your game state back to the begining of the game.  This allows you to play through the game multiple times')
        elif helpList[1].lower() == "mods" or helpList[1].lower() == "!mods":
            await ctx.channel.send(f'"!mods" is the command used to summon the human mods.  Use it when you feel like you need an adult or if the game seems broken')
        elif helpList[1].lower() == "cmd" or helpList[1].lower() == "!cmd":
            await ctx.channel.send(f'"!cmd" is the command used to send commands to the satellite.  If you have a question about a specific subcommand, type "!cmd help <subcommand>"')        
        elif helpList[1].lower() == "theme" or helpList[1].lower() == "!theme":
            await ctx.channel.send(f'!theme lets you change the background music')
        

    #await ctx.channel.send(f'Hello {ctx.author.name}: {CFG["text"]["help"]}')

# manages the user list locally, so that the chatbot can easily announce who the new controller is
def userThread():

    print("user thread running")

    tempUser = SatUser("temp")
    tempString = ""

    while True:
        for user in userList.getUserList():
            if (user.updateTimeout() >= 0):
                userList.setCurrentUser(user)

                print(f"Active user: {userList.getCurrentUser().getName()}")

                # Turns off smoke
                if userList.getCurrentUser().getCurrentStep() == 11: 
                    userList.getCurrentUser().setCurrentStep(12)

                simpleSatGame.reset(userList.getCurrentUser().getCurrentStep())
                tempString = f"The new active user is: {user.getName()}"
                asyncio.run(bot._ws.send_privmsg(bot.initial_channels[0], tempString))

                dispMan.updateUserList(userList.getNextUserList(5))

                time.sleep(60)
            else:
                userList.getUserList().remove(user)

                tempString = f"Removing {user.getName()} for inactivity"
                print(tempString)
                asyncio.run(bot._ws.send_privmsg(bot.initial_channels[0], tempString))
                #time.sleep(1)
                dispMan.updateUserList(userList.getNextUserList(5))

        # done to make sure current user is never null
        userList.setCurrentUser(tempUser)

if __name__ == "__main__":
    #t = threading.Thread(target=readThread, daemon=True)
    #t.start()

    t = threading.Thread(target=userThread, daemon=True)
    t.start()

    # dispMan.startDisplay(1920, 1080)
    dispMan.startDisplay(960, 540)

    bot.run()
