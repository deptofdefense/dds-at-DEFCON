# Code for running the chatbot controller for the defcon31 rover

from twitchio.ext import commands # needed for twitchIO chatbot
import openai # needed for ChatGPT API
from threading import Thread # needed for multithreading
import yaml # needed for config
import socket # needed for udp
import asyncio # needed for async thread

class ChatBot(commands.Bot):

    def __init__(self, accessToken, prefix, channelList, openAIkey, driveContext, lookContext):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...

        # UDP Sockets
        self.roverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Socket to send commands to rover
        self.roverAddress = ('rover.local', 7331)

        self.responseSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Dedicated socket to listen to rover responses
        self.responseSocket.bind(('0.0.0.0', 7331))

        # Starts listener socket thread
        self.responseThread = Thread(target=asyncio.run, args=(self.roverResponse(),), daemon=True)
        self.responseThread.start()

        openai.api_key = openAIkey
        self.driveContext = driveContext
        self.cameraContext = lookContext

        super().__init__(token=accessToken, prefix=prefix, initial_channels=channelList)


    async def roverResponse(self):

        while True: # Listen for response from rover
            data, addr = self.responseSocket.recvfrom(1024)

            reply = data.decode()

            if len(reply) > 0:
                print(reply)
                await self.connected_channels[0].send(f'{reply}')


    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        await self.connected_channels[0].send('Rover chatbot connected and listening!')

    async def event_join(self, channel, user):
        # Notify us when a new user joins the chat.  
        # We will send them a link to the instructions

        #print(f"User {user.name} joined")
        await self.connected_channels[0].send(f'Welcome {user.name}, instructions on how to play are at: https://github.com/zeetwii/llmRover#game-play')


    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return

        # Print the contents of our message to console...
        # print(message.content)

        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)

    # Hello command, kept in for the lulz
    @commands.command()
    async def hello(self, ctx: commands.Context):
        # Here we have a command hello, we can invoke our command with our prefix and command name
        # e.g ?hello
        # We can also give our commands aliases (different names) to invoke with.

        # Send a hello back!
        # Sending a reply back to the channel is easy... Below is an example.
        await ctx.send(f'Hello {ctx.author.name}!')

    # Move command, used to tell the rover where to go
    @commands.command()
    async def move(self, ctx: commands.Context):

        #print(ctx.message.content[5:]) # cut off the command part of the message
        userMessage = ctx.message.content[5:] # cut off the command part of the message

        # if user message not empty
        if len(userMessage) > 0:
            # Chat GPT stuff
            messages = [ {"role": "system", "content": self.driveContext} ]
            messages.append({"role": "user", "content": userMessage},)
            chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
            reply = chat.choices[0].message.content
            
            print(f"ChatGPT: {reply}")  
            try:
                self.roverSocket.sendto(str.encode(reply), self.roverAddress)
                await ctx.send(f'ChatGPT: {reply}')
            except:
                print("ERROR, unable to send to rover")
                await ctx.send(f'ERROR, Rover not responding.  Please yell at ZeeTwii')

    # Camera command, used to pan the camera
    @commands.command()
    async def look(self, ctx: commands.Context):
    
        #print(ctx.message.content[5:]) # cut off the command part of the message
        userMessage = ctx.message.content[5:] # cut off the command part of the message

        # if user message not empty
        if len(userMessage) > 0:
            # Chat GPT stuff
            messages = [ {"role": "system", "content": self.cameraContext} ]
            messages.append({"role": "user", "content": userMessage},)
            chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
            reply = chat.choices[0].message.content
            
            print(f"ChatGPT: {reply}")  
            try:
                self.roverSocket.sendto(str.encode(reply), self.roverAddress)
                await ctx.send(f'ChatGPT: {reply}')
            except:
                print("ERROR, unable to send to rover")
                await ctx.send(f'ERROR, Rover not responding.  Please yell at ZeeTwii')


    # Audio command, used to control background audio
    @commands.command()
    async def music(self, ctx: commands.Context):
        
        await ctx.send(f'audio command to be added')

    # Help command, used to ask for help
    @commands.command()
    async def help(self, ctx: commands.Context):
        
        await ctx.send(f'For background info on the game and how to play, please visit: https://github.com/zeetwii/llmRover#game-play')

if __name__ == "__main__":

    CFG = None  # global CFG settings
    with open("./configs/config.yml", "r") as ymlfile:
        CFG = yaml.safe_load(ymlfile)

    twitch_initial_channels = CFG["twitch"]["CHANNEL"]
    twitch_prefix = CFG["twitch"]["BOT_PREFIX"]
    twitch_access_token = CFG["twitch"]["ROVER_ACCESS_TOKEN"]

    openai_key = CFG["openai"]["API_KEY"]
    move_context = CFG["openai"]["MOVE_CONTEXT"]
    look_context = CFG["openai"]["LOOK_CONTEXT"]

    chatbot = ChatBot(twitch_access_token, twitch_prefix, twitch_initial_channels, openai_key, move_context, look_context)
    chatbot.run()
