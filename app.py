import os
import json

from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template

import util
import config
import wrapper

from IPython import embed

app = Flask(__name__)


DEFAULT_DEVICE = config.DEFAULT_DEVICE


@app.route('/')
def home():
    data = {"known_devices": config.KNOWN_DEVICES, "default_device": config.DEFAULT_DEVICE}
    return render_template("base.html", data=data)


@app.route('/ping')
def ping():
    return str(chromecast.check_status())

# Playback controls
@app.route('/play', methods=["GET", "POST"])
def play():
    # GET
    if request.method == "GET":
        return chromecast.play()  # Resume playback
    # POST
    uuid = request.get_json()['uuid']
    return chromecast.play(uuid)


@app.route('/pause')
def pause():
    return chromecast.pause()


@app.route('/stop')
def stop():
    return chromecast.stop()


@app.route('/ffwd')
def ffwd():
    return chromecast.ffwd()


@app.route('/rewind')
def rewind():
    return chromecast.rewind()


@app.route('/seek/<string:time>')
def seek(time):
    return chromecast.seek(time)


@app.route('/skip')
def skip():
    chromecast.skip()

# Volume
@app.route('/volume_up')
def volume_up():
    return chromecast.volume_up()


@app.route('/volume_down')
def volume_down():
    return chromecast.volume_down()


@app.route('/mute')
def mute():
    return chromecast.mute()

# Media/Inventory
@app.route('/media/list')
def media_list():
    with open("cache/media.json", "r") as f:
        return f.read()


@app.route('/select_device', methods=["POST"])
def select_device():
    chromecast.selected_device = request.get_json()["device"]
    return chromecast.selected_device


@app.route('/scan')
def scan():
    return json.dumps(chromecast.scan())


if __name__ == '__main__':
    chromecast = wrapper.Chromecast(config.DEFAULT_DEVICE)
    app.run(host="0.0.0.0", port="8000", debug=True)
