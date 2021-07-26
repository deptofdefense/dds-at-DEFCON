# Twitch Chatbot

## Setup

* `pip3 install twitchio`
* `pip3 install asyncio`
* `pip3 install pyserial`
* Copy config.yml.sample to config.yml and then populate config.yml with real credentials.
* Run the chat bot `python3 aerobot.py`

## Background

Created using [this guide](https://www.richwerks.com/index.php/2019/beginner-twitch-chatbot-using-python/).  

Goal is to use a bot to pull commands from a twitch chat and pass them to a server we control.  This will allow an audience to remotely control the defcon events.  

## Twitch chat bot setup
1. Need to generate a oAth Password [here](https://twitchapps.com/tmi/)
2. Register new Application (category chat bot) [here](https://dev.twitch.tv/console/apps)
