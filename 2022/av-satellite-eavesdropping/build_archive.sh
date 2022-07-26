#!/bin/bash
docker-compose down
rsync -a --delete .lab_templates/ lab_volume/
docker save -o docker-images.tar $(docker-compose config | awk '{if ($1 == "image:") print $2;}' ORS=" ")
tar --transform='s|[^/]*|satcoms_demo|' -czvf satcoms_demo.tar.gz ./docker_labs/ ./.lab_templates/ ./lab_volume/ ./docker-compose.yml ./reset_exercise.sh ./first_install.sh ./docker-images.tar ./get-docker.sh
rm ./docker-images.tar
