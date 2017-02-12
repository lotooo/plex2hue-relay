#
# Author: Matthieu Serrepuy <https://github.com/lotooo>
#
# App to manage your Phillips Hue light via the Plex webhooks
# https://support.plex.tv/hc/en-us/articles/115002267687-Webhooks  
#
import os
import sys
import json
from flask import Flask, abort, request
from qhue import Bridge, create_new_username

##################################
# ENV variables
##################################

try:
    flask_port = os.environ['FLASK_PORT']
except:
    flask_port = 5000

try:
    flask_debug = os.environ['FLASK_DEBUG']
except:
    flask_debug = False

# By default, we don't want to play with the lights if the player is not local
# But in case of Plex Cloud, we may want this option
try:
    local_player_only = os.environ['LOCAL_PLAYER_ONLY']
except:
    local_player_only = True

# MANDATORY : The bridge IP 
try:
    bridge_ip       = os.environ['BRIDGE_IP']
except:
    print('Unknown bridge IP. Please set it via env variable BRIDGE_IP')
    sys.exit(1)

#OPTIONNAL:A username (one will be created if needed, but it's better to save it
try:
    bridge_username = os.environ['BRIDGE_USERNAME']
except:
    print('Unknown bridge username. Creating one')
    bridge_username = create_new_username(BRIDGE_IP)
    print('Created %s. Please set it via env variable BRIDGE_USERNAME to avoid re-auth every restart')


# OPTIONNAL : Players UUID you want to filter on (not sure you want 
# to play with the living room light if a friend is watching something from
# your shared server at home
# This must be a comma separated list of uuid
try:
    filtered_players = os.environ['PLAYERS_UUID'].split(',')
except:
    filtered_players = None
    print('No specific player mentioned, your lights will blink !')

events = [
        'media.play', 
        'media.pause', 
        'media.resume', 
        'media.stop',
        'media.scobble',
        'media.rate'
]

# Retrieve the scene we want to activate for each event (based on env variable)
scene_for_event = {}
for event in events:
    if os.environ.has_key(event.upper().replace('.','_')):
        scene_for_event[event] = os.environ[event.upper().replace('.','_')]
    else:
        scene_for_event[event] = None


def activate_scene(scene_name):
    b = Bridge(bridge_ip, bridge_username)
    scenes = b.scenes()
    for scene_id, scene in scenes.items():
        if scene['name'] == scene_name:
            status = b.scenes[scene_id](http_method='get')
            lightstates = status['lightstates']
            # Check the current status of the lights
            # If every lights involved in this scene
            # are already off, don't change anything
            # It might means it is the day
            everything_is_off=True
            for light_id, light in lightstates.items():
                light_status = b.lights[light_id](http_method='get')
                if light_status['state']['on'] == True:
                    everything_is_off = False

            if everything_is_off:
                return False

            for light_id, light in lightstates.items():
                if light['on'] == True:
                    b.lights[light_id].state(on=True, bri=light['bri'], ct=light['ct'])
                else:
                    b.lights[light_id].state(on=False)
    return True

app = Flask(__name__)

@app.route("/", methods=['POST'])
def scene_root():
    # read the json webhook
    data = request.form

    try:
        webhook = json.loads(data['payload'])
    except:
        app.logger.error("No payload found")
        abort(400)

    app.logger.debug(webhook)

    # Extract the event
    try:
        event = webhook['event']
    except KeyError:
        app.logger.info("No event found in the json")
        return "No event found in the json"

    # Unless we explicitly said we want to enable remote players, 
    # Let's filter events
    if local_player_only:
        is_player_local = True # Let's assume it's true
        try:
            is_player_local = webhook['Player']['local']
        except:
            app.logger.info("Not sure if this player is local or not :(")
        if not is_player_local:
            app.logger.info("Not allowed. This player is not local.")
            return 'ok'

    # If we configured only specific players to be able to play with the lights
    if filtered_players:
        try:
            player_uuid = webhook['Player']['uuid']
        except:
            app.logger.info("No player uuid found")
            return 'ok'
        if not player_uuid in filtered_players:
            app.logger.info("%s player is not able to play with the lights" % player_uuid)
            return 'ok'

    # Extract the scene we are supposed to used with this event
    try:
        scene = scene_for_event[event]
    except KeyError:
        app.logger.info("%s is not a proper event" % event)
        return 'ok'

    # If we found a scene, let's activate it
    if scene:
        if activate_scene(scene):
            app.logger.info("%s scene activated" % scene)
            return 'ok'
        else:
            app.logger.info("%s scene not activated. Lights are currently off" % scene)
            return 'ok'
    else:
        app.logger.info("No scene to activate on %s" % event)
        return 'ok'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=flask_port, debug=flask_debug)
