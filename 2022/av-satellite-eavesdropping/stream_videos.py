#!/usr/bin/python3

"""
Very basic script to multiplex 2 videos together into a DVB-S2 stream

dependencies
brew install tsduck
"""

import subprocess, json
import argparse
import math
from subprocess import Popen, PIPE
import os

supress_stdout = True

def with_ffprobe(filename):
    """
    Function to get the duration (in seconds) of the provided video filename
    :param filename: the filename to check agaisnt
    :return: the duration of the video in seconds
    """
    result = subprocess.check_output(
            f'ffprobe -v quiet -show_streams -select_streams v:0 -of json "{filename}"',
            shell=True).decode()
    fields = json.loads(result)['streams'][0]

    duration = float(fields['duration'])
    return duration

def covert_to_MPEG_TS(filename_input, filename_output, service_name, service_id, start_pid, pmw_start_pid ):
    """
    Convert the provided filename into a MPEG-TS video
    :param filename_input: the filename input
    :param filename_output: the filename output
    :param service_name: Needs to be unique when streaming with other videos
    :param service_id: Needs to be unique when streaming with other videos
    :param start_pid: Needs to be unique when streaming with other videos
    :param pmw_start_pid: Needs to be unique when streaming with other videos
    :return: None
    """
    print(f"convert to MPEG TS the file: {filename_input} with file output: {filename_output}")
    service_provider = f"service_provider=HackerSat TV"
    service_name = f"service_name={service_name}"
    print(f"service_provider: {service_provider}, service_name:{service_name}")
    subprocess.run(['ffmpeg', '-i', filename_input, '-mpegts_service_id', service_id, '-mpegts_start_pid', start_pid,
                     '-mpegts_pmt_start_pid', pmw_start_pid, '-metadata', service_name, '-metadata', service_provider,
                     '-c', 'copy', '-f', 'mpegts', filename_output], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    print("convert to MPEG TS completed")


def multiplex_two_videos(video1, video2, output_name="challenge.ts"):
    """
    Convert the provided files video1 and video2 into a multiplexed DVB-S2 stream without output name.
    """
    cleanup_files = []  # List to keep track of what should be cleaned up prior to exiting

    #print(f"Multiplex 2 videos. Video 1: {video1}, Video 2: {video2}")

    video1_duration = with_ffprobe(video1)
    video2_duration = with_ffprobe(video2)

    # Determine which video needs to lengthen to match the other
    filename_to_lengthen = None
    filename_staying_same = None
    iteration_increase = 0
    trim_length = 0

    if video1_duration < video2_duration:
        filename_to_lengthen = video1
        filename_staying_same = video2
        iteration_increase = math.ceil(video2_duration / video1_duration)
        trim_length = video2_duration
    else:
        filename_to_lengthen = video2
        filename_staying_same = video1
        iteration_increase = math.ceil(video1_duration / video2_duration)
        trim_length = video1_duration

    #print(f"Found the shorter file: {filename_to_lengthen} with iterations: {iteration_increase} to eventually trim: {trim_length}")

    # Lengthen the shorter video to longer than the other
    subprocess.call(
        ['ffmpeg', '-stream_loop', str(iteration_increase), '-i', filename_to_lengthen, '-c', 'copy', 'tmp.mp4'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cleanup_files.append("tmp.mp4")
    #print(f"Lengthened the first video iteration count")

    # Now trim the excess of this video to match the length of the other
    subprocess.call(['ffmpeg', '-i', 'tmp.mp4', '-to', str(trim_length), '-c:v', 'copy', '-c:a', 'copy', 'tmp2.mp4'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cleanup_files.append("tmp2.mp4")

    #print(f"Increased the shorter filename to match.")

    # Convert the files into MPEG_TS streams each with unique information
    file_output_names = ['channel1.ts', 'channel2.ts']
    service_names = ["HackerSatTV One", "HackerSatTV Two"]
    service_id = ["1337", "2337"]
    start_pid = ["0x100", "0x200"]
    pmt_start_pid = ["0x1010", "0x1020"]

    i = 0
    covert_to_MPEG_TS('tmp2.mp4', file_output_names[i], service_names[i], service_id[i], start_pid[i],
                      pmt_start_pid[i])
    cleanup_files.append(file_output_names[i])
    i += 1
    covert_to_MPEG_TS(filename_staying_same, file_output_names[i], service_names[i], service_id[i], start_pid[i],
                      pmt_start_pid[i])
    cleanup_files.append(file_output_names[i])

    # Multiplex the streams together
    subprocess.run(
        ['tsp', '-d', '-I', 'file', '--interleave', file_output_names[1], file_output_names[0], '--label-base', '1', '-P',
         'psimerge', '--main-label', '1', '--merge-label', '2', '-P', 'svrename', service_id[0], '-n', service_names[0], '-P',
         'filter', '-n', '-p', '0x1FFF', '-O', 'file', output_name], shell=False)

    # Remove all of the videos used to build the final multiplexed stream
    for file in cleanup_files:
        #pass
        os.remove(file)

if __name__ == "__main__":

    # Collect the 2 video files to ultimately be multiplexed together
    parser = argparse.ArgumentParser(description='Process some videos together into a single stream.')
    parser.add_argument('--video1', help='the path to the first video')
    parser.add_argument('--video2', help='the path to the first video')
    parser.add_argument('--output', help='the final multiplexed output filename')

    args = parser.parse_args()

    if args.video1 and args.video2 and args.output:
        multiplex_two_videos(args.video1, args.video2, args.output)
    else:
        print(f"Error with command line arguments provided")
