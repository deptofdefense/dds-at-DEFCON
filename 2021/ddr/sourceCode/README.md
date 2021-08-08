# Rover

Message structure: left right time : +/-100 +/-100 0-255

motor format: first bit sign: 0 is positive, 1 is negative, last 7 represent precentage from 0 to 100
time format is 0 to 255 miliseconds times 10, ex: a value of 100 equals 1000 mS or 1 second



Run server:
cd to experimental library:

`export LD_LIBRARY_PATH=.`

`mjpg_streamer -i "input_raspicam" -o "output_http.so -w /usr/local/share/mjpg-streamer/www"`

or

`./mjpg_streamer -o "output_http.so -w ./www" -i "input_raspicam.so"`

On OBS add media source, remove local check box, enter:

`http://raspberrypi.local:8080/?action=stream`
