#!/bin/bash
rsync -a --delete .lab_templates/ lab_volume/
docker-compose down
xhost +local:
docker-compose up -d
docker-compose run lab_box bash