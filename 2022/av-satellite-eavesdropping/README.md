# Introduction to Satellite Eavesdropping

Satellite communications are used by millions of people every day. From television broadcasts to internet services, satellites bring connectivity to places where wired infrastructure doesn't reach.

In this lab, you’ll learn about one of the most popular satellite communications protocols - DVB-S (Digital Video Broadcasting for Satellite) - and how anyone with inexpensive radio equipment and freely available software can intercept and listen to these signals.

This lab was presented at the DEFCON30 Aerospace Village in 2022.

## Why This Matters
It has been demonstrated that hackers can use some of the techniques in this lab to gain access to critical infrastructure control systems (e.g. power plants), eavesdrop on sensitive emails at distances of thousands of miles away from their victims, and even compromise critical in-flight data links on modern aircraft.

If you're curious, check out this video to learn more: https://www.youtube.com/watch?v=ku0Q_Wey4K0


# First Time Setup

1) To configure this lab to run for the first time you will need to clone this repository and run the `first_install.sh` script. This script has been tested on a default install of Ubuntu 20.04 but may need to be adapted for your environment. It installs the latest version of Docker and Docker-Compose. Older versions, such as those in your distros apt repository, may not work appropriately.

If you want to have the pre-configured `/lab_resources` mount point work out of the box (not necessary for this lab, but nice to have), you'll need to copy the contents of this directory into a folder named `~/sat_carving_lab/`.

2) After running the install script, you may need to log out and log back in to enable the `docker` group on your user account.

3) Once you've run the install script press `CTRL+C` to stop the docker containers and then run `reset_exercise.sh` to launch the lab and open a shell inside the simulation environment.


# Lab Handout / Guide
This lab assumes no familiarity with the linux shell, satellites, or radio communications. The guide below can be printed off as a handout and provided to participants or used as a step-by-step guide to running the exercise yourself. You will still need to complete the "First Time Setup" instructions above to be able to run the lab.
## Getting Started
### Introduction to the Linux Shell

In these labs, we will be using command-line tools from within a Linux shell. Lots of computer programs and hacking tools lack point-and-click user interfaces and instead rely on the shell for execution.

If you've never worked with a shell line before, don't worry, we'll keep things simple.

A `shell` is a special program for giving instructions to your computer. You use a shell by typing in a series of `commands` and pressing the `ENTER` key to execute them.

In this lab, you will occasionally need to `interrupt` commands which you have run. For example, you may want to stop a radio recording and look at the data that you've captured. In a shell, you can do this by entering the shortcut `COMMAND+C`.

One of the most powerful features of a shell is the ability to combine commands together. In this lab, we'll do this using the `pipe` operator, which is this symbol: `|`. You'll find it below the `BACKSPACE` or `DELETE` key on your keyboard and will typically have hold down the `SHIFT` key to type it.

### Step 1: Opening a Shell
Open your shell by pressing the `CTRL+ALT+T` keys at the same time. You can also open a shell by clicking the app launcher in the bottom left corner of your screen and searching for the `terminal` app.

### Step 2: Navigate to the Lab
Type the following command into your terminal and then hit `ENTER`. Remember to type commands exactly as they appear in this guide or they may not work. (Note the `~` character is towards the top left corner of your keyboard, below the `ESC` key. You will typically need to press `SHIFT` to type it.)

```bash
cd ~/satcoms_demo/
```

This command tells your computer to open the folder which contains the satellite lab we'll be working on.

### Step 3: Launch the Lab Exercise
In this lab, we'll be connecting to a virtual satellite workstation. To do this, just run the following command.

```bash
./reset_exercise.sh
```

You'll see some output on the screen and after a few seconds you'll see a slightly different looking `shell` running on your laptop. This shell is inside the satellite workstation simulator.

## Exploring Radio Signals

Since we're indoors, you won't be able to hear any real satellites - even if you had the appropriate radio hardware (which costs about $300 if you're wondering). Instead, we'll listen to a simulated radio signal that's in the same format as you'd get from a real satellite.

### Step 4: Listen to the Satellite
You can take a look at the data you get from the device by running this command:

```bash
nc localhost 8118 | xxd
```

You should see a lot of numbers and letters scrolling across the screen. These represent the physical properties of the radio signal - similar to how a satellite dish might encounter these signals over the air. Our task today will be to convert these physical properties into meaningful information.

When you're done looking at the signal press `CTRL+C` to `interrupt` your listener. This should return you to the shell.

### Step 5: Demodulate the Signal

We are going to use a signal demodulator to convert these radio signals into bits and bytes that a computer can understand. Specifically, we'll be using a program called `leandvb` which is freely available and designed for working with satellite feeds.

`leandvb` will take the physical properties of the radio waves (essentially the shape and size of the "wiggles" that you'd see in a graph of the radio wave), and convert those into different numerical values. We can actually see how LeanDVB converts the radio wave into one of four values using the following command:

```bash
nc localhost 8118 | leandvb --standard DVB-S2 --f32 -f 4e6 --gui > /dev/null
```

*Note: Don't worry too much about the parameters of this command, the --f32 and -f 4e6 parts are just properties of the radio hardware we're receiving the satellite signal with. The rest of the command details what protocol to use and where to save the output data from the tool.*

After a few seconds, you'll see some graphs depicting the radio signal you have tuned to. Note the distinct circles on the graph in the bottom left corner, these relate to the values that your demodulator is mapping the radio wave to in a `constellation`. Using this constellation and some specific rules, your computer can convert the physical properties of the radio wave into bits and bytes.

### Step 6: Record Some Data

Let's go ahead and use `leandvb` to save some of this converted data to our computer so we can look at it. Go ahead and run the following command:

```bash
nc localhost 8118 | leandvb --standard DVB-S2 --f32 -f 4e6 > my_recording.ts
```

Wait about 30 seconds, so that you can save a decent amount of data, and then press `CTRL+C` to stop recording data from the satellite. Don't worry if you see some error messages.

### Step 7: Explore Your Recording

You've just created a new file called `my_recording.ts` which contains your recording. We're going to use a tool called `tsanalyze` to convert this data into a format called `MPEG-TS`.

Run the following command to see a summary of the data that you've just captured:

```bash
tsanalyze my_recording.ts
```

You can scroll through this data with `SPACE`. Go ahead and read the output and see if you can make some sense of what's going on.

The main thing to pick up on here is that there are two programs in this satellite feed: `HackerSatTV One` and `HackerSatTV Two.` Both of these programs appear to have `AVC encoded video data`, suggesting that they might be video streams. Let's see if we can snoop on them!

### Step 8: Watch Your Recording

To watch the satellite feed you just recorded, we're going to use a tool called `tsp` which is similar to `tsanalyze` that we used above, but allows us to actually manipulate the `MPEG-TS` data we're receiving in various ways.

Let's run a command to take our `my_recording.ts` file and look at it in tsp:

```bash
cat my_recording.ts | tsp -P zap "HackerSatTV One" -O play
```

After a few seconds, a video should pop up based on the content of the file you've recording. It'll probably be pretty short, since you only recorded a few seconds of data.

Go ahead and close out your recording. If the video player doesn't close, you can move it over a bit and press `CTRL+C` in your terminal to close it instead.


### Step 9: Watch the Live Satellite

Now that we've verified that there's a video in our data capture, the final step is tap into the live satellite signal and watch it in real time.

Run the following command to connect everything you've done in this lab into a single step:

```bash
nc localhost 8118 | leandvb --standard DVB-S2 --f32 -f 4e6 | tsp -P zap "HackerSatTV One" -O play
```

If you've done everything right, you should be able to intercept satellite video streams through your own DVB-S signal processing pipeline. Congrats!


# Custom Videos

If you want to run this exercise with your own videos, you'll need to build a .ts stream from the media that you record and multiplex the videos with ffmpeg.

### SETUP: Create .ts streams for each channel

You can convert .mp4 files into .ts files using ffmpeg so that they can be multiplexed by tsduck in the next step.

#### Easy Script
Provided you have the requisite dependencies installed.
```bash
brew install tsduck
```

You can run the following script to multiplex your videos together.

```bash
python3 stream_videos.py --video1 video1.filename --video2 video2.filename --output challenge.ts
``` 

You should find the duration of your longest .mp4 file and remember that. For each of your other files, you should determine how many repetitions will be required to exceed that length and then run loop and trim using ffmpeg. The goal is to have all of your files be the same length before multiplexing:
```bash
ffmpeg -stream_loop [number of interations] -i satcoms_channel_1.mp4 -c copy channel_1_long.mp4

ffmpeg -i channel_1_long.mp4 -to [desired time, e.g. 13:37] -c:v copy -c:a copy channel_1_final.mp4
```

Next you will convert the mp4 containers to mpeg streams. If you wish to reduce the overall size of the video before combining the streams you can re-encode the mp4's at this stage. For example, to halve the resolution you can do the following. This will take a few minutes to encode.
```bash
ffmpeg -i channel_1_final.mp4 -vf "scale=iw/2:ih/2" channel_1_reduced.mp4
```

Next convert each mp4 file into a MPEG-TS stream. You should ensure that the service name, service_id, start_pid, and pmt_start_pid are unique to prevent conflicts when multiplexing:
```bash
ffmpeg -i channel_2_reduced.mp4 -mpegts_service_id 2337 -mpegts_start_pid 0x200 -mpegts_pmt_start_pid 0x1020 -metadata service_name="HackerSatTV Two" -metadata service_provider="HackerSat TV" -c copy -f mpegts channel2.ts
```

### SETUP: Create raw .ts feed
You can then multiplex your streams into a single satellite telvision station transponder MPEG-TS using tsduck. The easiest way to do this if you only have two streams is to use the ``--interleave`` and ``psimerge`` options. If you have more than two streams it is significantly more complex, the main thing to keep in mind is the base stream for a ``merge`` needs to have sufficient padding to support the additional streams added.

Typically, when using --psimerge, you want to designate the base feed as the one which is most sensitive to bitrate (e.g. if only one has audio). You also need to manually add entries to the service table with svrename for any non-base services you are adding.

```bash
tsp -I file --interleave channel2.ts channel1.ts --label-base 1 -P psimerge --main-label 1 --merge-label 2 -P svrename 1337 -n "HackerSatTV One" -P filter -n -p 0x1FFF -O file challenge.ts
```

To validate that your feed is appropriate, run the following command on a linux system with vlc installed, replacing "HackerSatTV One" with the service name of a service in your feed. Try this for all services. After a few seconds, VLC should sync to the output and begin displaying video.
```bash
tsp -I file challenge.ts -P zap "HackerSatTV One" -O file station.ts
```
