#!/bin/bash

# This script executes the manage.py script in the django docker container.

# Note: This script is set up to run on the production server. If you want to run it on your local machine, you will need to change the paths.

DOCKER_COMPOSE_FILE=$1                                              # This is the path to the docker-compose file.
COMMAND=$2                                                          # This is the command to execute.

/usr/local/bin/docker-compose -f $DOCKER_COMPOSE_FILE exec -T django python manage.py $COMMAND
