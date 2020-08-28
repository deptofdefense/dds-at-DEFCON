# aerobot.py
# Created for defcon28 aerospace village

import threading    # needed for threading
import time         # needed for sleep
import binascii     # needed for serial
import yaml         # needed for config
import asyncio      # needed for async ops
import argparse

from twitchio.ext import commands           # from tutorial, for twitch
from BricksInTheAir import BricksInTheAir   # needed to manage game
from UserList import UserList               # needed for user management
from BrickUser import BrickUser             # needed for user management

from gameDisplay import DisplayManager  # needed for running the game overlay

from PyQt5.QtCore import Qt # needed for gui
from PyQt5.QtGui import *  # needed for gui
from PyQt5.QtWidgets import * # needed for gui

CFG = None  # global CFG settings

with open("config.yml", "r") as ymlfile:
    creds = yaml.safe_load(ymlfile)

with open(creds["script"], "r") as scriptfile:
    script = yaml.safe_load(scriptfile)

CFG = {**creds, **script}

# pulling the values from config.yml
# keeping them separate for flexibilitycode sharing
bot = commands.Bot(
    irc_token = CFG["twitch"]["TMI_TOKEN"],
    client_id = CFG["twitch"]["CLIENT_ID"],
    nick = CFG["twitch"]["BOT_NICK"],
    prefix = CFG["twitch"]["BOT_PREFIX"],
    initial_channels = CFG["twitch"]["CHANNEL"]
)

# manages the game
bia_game = BricksInTheAir(CFG)

# Display Manager to handle overlay
dispMan = DisplayManager(CFG)

# user list for managing active connections
userList = UserList(CFG, dispMan, bia_game, bot)
userList.startUserThread()


# bot connection event
@bot.event
async def event_ready():

    global CFG, bia_game, userList, dispMan

    print(CFG["twitch"]["BOT_NICK"] + " is online!")
    ws = bot._ws
    await ws.send_privmsg(bot.initial_channels[0], f"/me is now operational")
    #userList.triggerChanges()


# event for user entering something in chat
@bot.event
async def event_message(ctx):
    global CFG, bia_game, userList, dispMan

    if ctx.author.name.lower() == CFG["twitch"]["BOT_NICK"].lower():
        return
    await bot.handle_commands(ctx)
    print(f'{ctx.channel} - {ctx.author.name}: {ctx.content}')


# reset command - proof of concept
@bot.command(name='reset')
async def reset(ctx):
    global CFG, bia_game, userList, dispMan

    if ctx.author.name in CFG["admins"]:
        userList.emptyUserList()
        bia_game.reset_board()
        bia_game.set_engine_speed(0, True)

        await ctx.channel.send(f"{ctx.author.name} sent the command reset")
    #else:
        #await ctx.channel.send(f"{ctx.author.name}: nope")


# generic command - meant to be flexible
@bot.command(name='cmd')
async def cmd(ctx):
    global CFG, bia_game, userList, dispMan

    currentUser = userList.getCurrentUser()
    if currentUser != None:
        if currentUser.matchName(ctx.author.name):
            currentUser.resetTimeout()
            msg = bia_game.checkCmd(currentUser, ctx.content[5:])
            #dispMan.updateCmdMsg(ctx.content)
            userList.triggerChanges(prologue=True, cmd=ctx.content)
            await ctx.channel.send(f"{ctx.author.name} {msg}")
            #await bot._ws.send_privmsg(bot.initial_channels[0], msg)
            await ctx.channel.send(f"Question: {userList.getCurrentUser().getQuestion()}")
            #await bot._ws.send_privmsg(bot.initial_channels[0], f"Question: {userList.getCurrentUser().getQuestion()}")
        else:
            await ctx.channel.send(f"{ctx.author.name}, it is not your turn.")
            #await bot._ws.send_privmsg(bot.initial_channels[0], "It is not your turn, please be patient.")
    else:
        await ctx.channel.send(f"{ctx.author.name}, it is not your turn.")
        #await bot._ws.send_privmsg(bot.initial_channels[0], "It is not your turn, please be patient.")


# join command - allows user to join the user list
@bot.command(name='join')
async def join(ctx):
    global CFG, bia_game, userList, dispMan

    if userList.addUser(ctx.author.name):
        if len(userList.getUserList()) == 1:
            await ctx.channel.send(f"{ctx.author.name} has joined the user list for this challenge and is now the active user.")
            currentUser = userList.getCurrentUser()
            if currentUser != None:
                await ctx.channel.send(f"Question: {userList.getCurrentUser().getQuestion()}")
                #await bot._ws.send_privmsg(bot.initial_channels[0], f"Question: {currentUser.getQuestion()}")
            userList.triggerChanges(prologue=True, cmd=ctx.content)
        else:
            await ctx.channel.send(f"{ctx.author.name} has joined the user list and will show as active soon.")
            userList.triggerChanges(prologue=False)
    else:
        await ctx.channel.send(f"{ctx.author.name}, there are too many people in the active cue... try to join again soon.")

# leave command - allows user to leave the user list before they timeout
@bot.command(name='leave')
async def leave(ctx):
    global CFG, bia_game, userList, dispMan

    print("leave cmd sent")
    currentUser = userList.getCurrentUser()
    if currentUser != None:
        if currentUser.matchName(ctx.author.name):
            # the active user is trying to leave. Resart userThread
            userList.removeUser(ctx.author.name)
            userList.restartUserThread()
            await ctx.channel.send(f"{ctx.author.name} has left the user list.")
            #await bot._ws.send_privmsg(bot.initial_channels[0], "Thanks for playing.")

        elif userList.removeUser(ctx.author.name):
            await ctx.channel.send(f"{ctx.author.name} has left the user list.")
            #await bot._ws.send_privmsg(bot.initial_channels[0], "Thanks for playing.")
            userList.triggerChanges(prologue=False)
    else:
        await ctx.channel.send(f"{ctx.author.name}, you are not on the user list.")
        #await bot._ws.send_privmsg(bot.initial_channels[0], "Don't leave yet... !join first.")

# help command - link to repo readme with instructions
@bot.command(name='help')
async def help(ctx):
    global CFG, bia_game, userList, dispMan

    msg = f'Hello {ctx.author.name}: {CFG["text"]["help"]}'
    await ctx.channel.send(f'Hello {ctx.author.name}: {CFG["text"]["help"]}')
    #await bot._ws.send_privmsg(bot.initial_channels[0], msg)

@bot.command(name='hint')
async def hint(ctx):
    global CFG, bia_game, userList, dispMan

    currentUser = userList.getCurrentUser()
    if currentUser != None:
        if currentUser.matchName(ctx.author.name):
            currentUser.resetTimeout()
            msg = currentUser.getHint()
            #dispMan.updateCmdMsg(ctx.content)
            await ctx.channel.send(f"{ctx.author.name}: {msg}")
            #await bot._ws.send_privmsg(bot.initial_channels[0], msg)
        else:
            await ctx.channel.send(f"{ctx.author.name}, it is not your turn to ask for a hint.")
            #await bot._ws.send_privmsg(bot.initial_channels[0], "It is not your turn to ask for a hint.")
    else:
        await ctx.channel.send(f"{ctx.author.name}, it is not your turn to ask for a hint.")
        #await bot._ws.send_privmsg(bot.initial_channels[0], "It is not your turn to ask for a hint.")

@bot.command(name='goto')
async def goto(ctx):
    global CFG, bia_game, userList, dispMan

    currentUser = userList.getCurrentUser()
    if currentUser != None:
        if currentUser.matchName(ctx.author.name):
            currentUser.resetTimeout()
            msg = None
            try:
                step = str(ctx.content[6:]).lower()
                msg = currentUser.setCurrentStep(step)
                userList.triggerChanges(prologue=True, cmd=ctx.content)
            except Exception as err:
                print(repr(err))

            if msg != None:
                await ctx.channel.send(f"{ctx.author.name}: {msg}")
                await ctx.channel.send(f"Question: {userList.getCurrentUser().getQuestion()}")
                #await bot._ws.send_privmsg(bot.initial_channels[0], msg)

        else:
            await ctx.channel.send(f"{ctx.author.name}, it is not your turn to goto another step.")
            #await bot._ws.send_privmsg(bot.initial_channels[0], "It is not your turn to goto another step.")
    else:
        await ctx.channel.send(f"{ctx.author.name}, it is not your turn to goto another step.")
        #await bot._ws.send_privmsg(bot.initial_channels[0], "It is not your turn to goto another step.")

@bot.command(name='question')
async def question(ctx):
    global CFG, bia_game, userList, dispMan

    currentUser = userList.getCurrentUser()
    if currentUser != None:
        if userList.getCurrentUser().matchName(ctx.author.name):
            msg = currentUser.getQuestion()
            #dispMan.updateCmdMsg(ctx.content)
            currentUser.resetTimeout()
            await ctx.channel.send(f"{ctx.author.name}: {msg}")
            #await bot._ws.send_privmsg(bot.initial_channels[0], msg)
        else:
            await ctx.channel.send(f"{ctx.author.name}, it is not your turn to ask for a question.")
            #await bot._ws.send_privmsg(bot.initial_channels[0], "It is not your turn to ask for a question.")
    else:
        await ctx.channel.send(f"{ctx.author.name}, it is not your turn to ask for a question.")
        #await bot._ws.send_privmsg(bot.initial_channels[0], "It is not your turn to ask for a question.")

@bot.command(name='pause')
async def pause(ctx):
    # store state of current userList. Perhaps useful for a hard restart
    if ctx.author.name in CFG["admins"]:
        #bot.initial_channels[0].send("TEst")
        print(type(ctx))
        print(ctx)
        await ctx.channel.send(f"{ctx.author.name} sent the pause command")
    else:
        await ctx.channel.send(f"{ctx.author.name}: nope")


@bot.command(name='restore')
async def restore(ctx):
    # store state of current userList. Perhaps useful for a hard restart
    if ctx.author.name in CFG["admins"]:
        await ctx.channel.send(f"{ctx.author.name} sent the restore command")
    else:
        await ctx.channel.send(f"{ctx.author.name}: nope")

if __name__ == "__main__":
    #dispMan.startDisplay()
    bot.run()
