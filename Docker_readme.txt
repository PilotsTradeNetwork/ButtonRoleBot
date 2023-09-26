# To build a new docker image

$ docker build -t yourname/buttonrolebot:latest .

# To run in a container

Make a local dir to store your .env and database files

$ mkdir /opt/buttonrolebot
$ cp .env /opt/buttonrolebot/

Run the container:

$ docker run -d --restart unless-stopped --name buttonrolebot -v /opt/buttonrolebot:/root/buttonrolebot yourname/buttonrolebot:latest
