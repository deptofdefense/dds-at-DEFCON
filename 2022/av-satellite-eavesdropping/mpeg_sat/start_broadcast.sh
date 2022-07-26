#!/bin/bash
while true; do cat /home/dvb/bin/challenge.ts; done | leandvbtx --standard DVB-S2 | nc -lk 8118