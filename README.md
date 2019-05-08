# Cyads Processor

This project processes the ads that has been saved by the bots. The ads 
are watched by the bots are saved either in .xml or .json format. The process 
works in real time and uses Google pub-sub for real time processing. 

A Google Topic is made on Google pub-sub where bots send the real time events. Cyads 
processor subscribes to that Topic on Google cloud and keeps listening to the topic for 
the events. When a event happens, Batch Subscriber takes the required action depending 
upon the event type.


Following are the steps that are involved:

1) Bots send batch started message into the Google Pub-Sub Topic.

2) Batch processor sees the batch started message in topic and its saves the batch information
in the database. This will make the Dashboard real time. Whenever a batch is started, its status 
will appear in the dashboard.  

3) Bots watch the videos on youtube and save either .xml or .json file for the ads found.
Note that the files are being saved into the into the machine where it has been 
running. The saved files contains the information about the ad.

4) When the batch is completed the batch completed message is sent to the topic by the bots.

5) Processor will update the database information after receiving batch completed message.
This will update the dashboard too.

6) After the batch is completed, bots sync the data from their machine to the processing
server. After the data is synced, bots send a message in the topic with batch synced
event.

7) After receiving batch synced event, processor parses the files and saves it into the 
database.

Example payload of the events that are received in the topic.

# Batch Started
{
  "event": "batch_started",
  "bots_started": 90,
  "hostname": "765a89b91f33",
  "run_id": 1530805573,
  "host_hostname": "node10.misc.iastate.edu",
  "external_ip": "129.186.252.113",
  "location": "new_one",
  "timestamp": 1530705574,
  "video_list_size": 20
}

# Batch Completed

{
  "hostname": "765a89b91f33",
  "event": "batch_completed",
  "run_id": 1530805573,
  "host_hostname": "node10.misc.iastate.edu",
  "external_ip": "129.186.252.113",
  "location": "from container",
  "status": "COMPLETE",
  "ads_found": 20,
  "requests": 5500,
  "timestamp": 1530742703
}
  
  
# Batch Synced

{
 "event": "batch_synced",
 "batch_info": {
   "hostname": "01b173e35f17",
   "event": "batch_completed",
   "run_id": 1533349661,
   "host_hostname": "node1.misc.iastate.edu",
   "external_ip": "192.187.101.186",
   "location": "florida",
   "status": "COMPLETE",
   "video_list_size": 551,
   "bots_in_batch": 8,
   "ads_found": 15126,
   "requests": 44000,
   "timestamp": 1530804549
 },
 "kind": "COMPLETE",
 "data": {
   "kind": "COMPLETE"
 }
}


# Running the processor on local machine

To run the processor, we need to set some environment variables at first:

TOPIC_SUBSCRIPTION_NAME=dev
GOOGLE_KEY=<replace with google api key>
DATABASE_HOST= localhost
SECRET_KEY=sko9&g@@kn4+k$\=xp8khbdvxdil6!@tekk!@lr_!qtmjb-$&xe
dump_path=<path where files from the bots are saved>
GOOGLE_TOPIC=development
DEBUG=True
GOOGLE_APPLICATION_CREDENTIALS=<Googles credentials.json file for the account with topic>
DJANGO_SETTINGS_MODULE=CyadsProcessor.settings
PYTHONUNBUFFERED=1
DATABASE=cyads_processor
ALLOWED_HOST=127.0.0.1
GOOGLE_PROJECT_ID=cyads-203819
DATABASE_PASSWORD=
DATABASE_USER=root

Finally Run the following command.

python manage.py runserver 8000


# Building the docker image and pusing it into the docker hub

To build the image and push the image into the docker hub, use following command:


docker build -t cyads_processor .
docker image ls
tag <image id of the latest found from above command> <docker hub user>/cyads_processor:<version>
docker push <username>/cyads_processor


# Running the processor on local machine using docker

Go to the root directory of the project and run the following command:


docker run --net="host" -p 80:8000 \
-e TOPIC_SUBSCRIPTION_NAME=dev \
-e GOOGLE_TOPIC=development \
-e GOOGLE_PROJECT_ID=cyads-203819 \
-e GOOGLE_APPLICATION_CREDENTIALS=/opt/.key/<google credential file>.json \
-e SECRET_KEY=asdadada65656asd65a65asdaasdasdasdadasdasdasdas9755 \
-e DEBUG=False \
-e DATABASE=cyads_processor \
-e DATABASE_HOST=127.0.0.1 \
-e DATABASE_USER=root \
-e DATABASE_PASSWORD='root' \
-e ALLOWED_HOST=localhost \
-e GOOGLE_KEY=<Google Api Key> \
-e DUMP_PATH=/opt/dumps/ \
--mount type=bind,source=<path where synced files are saved>,target=/opt/dumps \
--mount type=bind,source=<path where credential.json file is saved>=/opt/.key \
--mount type=bind,source=<path where logs will be saved>,target=/opt/CyadsProcessor/logs <dockerhub user>/cyads_processor:<version>


















