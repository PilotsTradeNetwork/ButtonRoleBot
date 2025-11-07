FROM python:3.10-slim-bookworm
RUN apt-get update && apt-get install -y git
#This is getting a 'bleeding edge' version
#RUN pip3 install -U git+https://github.com/Rapptz/discord.py
RUN mkdir -p /usr/src/bot
WORKDIR /usr/src/bot
COPY setup.py .
COPY README.md .
COPY ptn ptn
RUN pip3 install .
RUN mkdir /root/buttonrolebot
RUN ln -s /root/buttonrolebot/.env /root/.env
WORKDIR /root/buttonrolebot
ENTRYPOINT ["/usr/local/bin/buttonrolebot"]
