set -ex
# SET THE FOLLOWING VARIABLES
# docker hub username
USERNAME=testcyads
# image name
IMAGE=cyads_processor
docker build -t $USERNAME/$IMAGE:latest .
