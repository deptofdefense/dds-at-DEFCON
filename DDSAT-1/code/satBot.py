# aerobot.py
# Created for defcon28 aerospace village

import yaml # needed for config
from twitchio.ext import commands # from tutorial, for twitch
import threading # needed for threading
import time # needed for sleep
import asyncio # needed for async ops

from ddSat import DDSat # needed for game


CFG = None  # global CFG settings
with open("config.yml", "r") as ymlfile:
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

# set up game
ddsat1 = DDSat(CFG["hardware"]["PAY01"], CFG["hardware"]["PAY02"])

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
@bot.command(name='msg')
async def msg(ctx):

    msgList = str(ctx.content).split()

    if len(msgList) > 1:
        response = ddsat1.processCmd(msgList[1])
        await ctx.channel.send(f"!rsp {response}")
    else: 
        response = "Error, incorrect use of !msg"
        await ctx.channel.send(f"{ctx.author.name}: {response}")

    



def statThread():
    ''' periodically prints status message '''

    print("status thread running")

    while True:

        tempString = f"!status {ddsat1.statusCheck()}"

        try:
            asyncio.run(bot._ws.send_privmsg(bot.initial_channels[0], tempString))
        except:
            print("whoops")


        time.sleep(300)


if __name__ == "__main__":

    threading.Thread(target=statThread, daemon=True).start()

    bot.run()