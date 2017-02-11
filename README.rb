plex2hue-relay
==============

plex2hue-relay is a small python app based on Flask + qhue acting as proxy between Plex Media Server webhooks and the Philips Hue Bridge.

Based on:
* Flask : http://flask.pocoo.org/
* Qhue : https://github.com/quentinsf/qhue

# Installation

## CLI

```
git clone https://github.com/lotooo/plex2hue-relay.git
cd plex2hue-relay
pip install -r requirements.txt
```

## Docker
```
git clone https://github.com/lotooo/plex2hue-relay.git
cd plex2hue-relay
docker build . -t lotooo/plex2hue-relay
```

## Dockerhub
```
docker pull lotooo/plex2hue-relay
```

# Environment variables
Name|Usage|Mandatory
----|-----|---------
BRIDGE_IP|Philips Hue bridge IP|Mandatory
BRIDGE_USERNAME|Bridge API username|Optional (it will generate one for you)
FLASK_PORT|Port flask should listen on|Optional
PLAYERS_UUID|Comma separated list of player uuid you want to filter (to avoid lighting up your living room while watching in your room|Optional
LOCAL_PLAYER_ONLY|By default we filters the event to local players only. In case of Plex Cloud, you can force to remove this filter|Optional
MEDIA_PLAY|Scene to activate when the event media.play is triggered|Optional
MEDIA_STOP|Scene to activate when the event media.stop is triggered|Optional
MEDIA_RESUME|Scene to activate when the event media.resume is triggered|Optional
MEDIA_PAUSE|Scene to activate when the event media.pause is triggered|Optional
MEDIA_SCROBBLE|Scene to activate when the event media.scrobble is triggered|Optional
MEDIA_RATE|Scene to activate when the event media.rate is triggered|Optional

# Usage

## CLI

```
export BRIDGE_IP=X.X.X.X
export BRIDGE_USERNAME=xxxxxxxxxxxxxxxxxxxxxx
export MEDIA_PLAY=Plex
export MEDIA_STOP=Lumineux
export MEDIA_RESUME=Plex
export MEDIA_PAUSE=Lumineux
python plex2hue.py
```

## Doccker
```
sudo docker run -d --name plex2hue-relay \
    -p 5000:5000 \
	-e BRIDGE_IP=X.X.X.X \
	-e BRIDGE_USERNAME=xxxxxxxxxxxxxxxxxxxxxx \
	-e MEDIA_PLAY=Plex \
	-e MEDIA_STOP=Lumineux \
	-e MEDIA_RESUME=Plex \
	-e MEDIA_PAUSE=Lumineux \
    lotooo/plex2hue-relay
```
