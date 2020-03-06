import re
import os
import json
import util
import subprocess

import config

from IPython import embed
import logging

"""
F using the API for now, just build a wrapper around the CLI bc fast and easy and
the API isn't really working and isn't complete.
"""


class Chromecast():
    def __init__(self, name):
        # self.devices = self.scan()  # Find and set self.devices
        self.selected_device = config.DEFAULT_DEVICE

    def _run_cmd(self, cmd, args=[], omit_device_name=False):
        # @todo: Address this potential RCE before release
        print("_run_cmd, cmd={}, args={}".format(cmd, args)) # why is logging.debug() not showing up?
        run_me = ["catt"]
        if not omit_device_name:  # device name is specified
            try:
                run_me += ["-d", self.selected_device]
            except AttributeError:
                pass
        run_me += [cmd] + args
        if cmd.lower() == "cast":
            self.play_background_proc = subprocess.Popen(run_me)
            return "200"
        return subprocess.check_output(run_me).decode("utf-8")

    def check_status(self):
        try:
            status = self._run_cmd("status")
        except Exception as e:
            return {"error": str(e)}

        # Title
        title = re.search("Title: (.+?)\n", status)
        self.title = os.path.splitext(title.group(1))[0] if title else None
        # Time
        time = re.search(r"Time: ([0-9:]+?)\s/\s([0-9:]+?)\s", status)
        self.current_time = time.group(1) if time else None
        self.end_time = time.group(2) if time else None
        # State
        state = re.search("State: (.+?)\n", status)
        self.state = state.group(1) if state else None
        # Volume
        volume = re.search("Volume: (.+?)\n", status)
        self.volume = volume.group(1) if volume else None

        status = {"title": self.title, "current_time": self.current_time,
                  "end_time": self.end_time, "state": self.state,
                  "volume": self.volume, "device": self.selected_device}
        self.update_history(status)
        return status

    def update_history(self, status):
        with open("cache/media.json", "r") as f:
            # @todo: Improve this; maybe there should be a history.json
            media = json.loads(f.read())
            for i, d in enumerate(media):
                if d["title"] == status["title"]:
                    media[i]["history"] = status
                    break
            if media[i]["history"]:
                with open("cache/media.json", "w") as f:
                    f.write(json.dumps(media, indent=4))

    # Playback
    def play(self, uuid='', with_subtitles=config.DEFAULT_SUBS):
        print("Play UUID: {}".format(uuid if uuid else "UUID missing"))
        if not uuid:
            return self._run_cmd("play")

        try:
            filepath = util.search_media('uuid', uuid)[0]['path']
        except IndexError:
            err_txt = "Error playing file. UUID {} not found in {}\n \
            Try hard-refreshing the browser to flush the cache;\n \
            the media library was reindexed so media.json must be \
            refreshed".format(uuid, config.MEDIA_BASE_DIR)
            print(err_txt)
            return err_txt

        if not os.path.isfile(filepath):
            err_txt = "Error playing file. File not found: {}".format(filepath)
            err_txt += "\nIs the media Drive mounted?"
            err_txt += "\n$ mkdir /tmp/media; sudo mount -t cifs -o username=guest //192.168.1.203/D /tmp/media"
            print(err_txt)
            return err_txt

        args = []
        if filepath.endswith(".mkv") and with_subtitles:  # @todo: improve this
            subs = util.process_mkv(filepath)
            if subs:
                args += ["-s", subs]
        args.append(filepath)

        # replace /Volumes/D/ with /tmp/media in some intelligent fashion
        # mkdir -p /Volumes/D; ln -s /Volumes/D /tmp/media

        print("calling _run_cmd({}, {})".format("cast", args))
        return self._run_cmd("cast", args)

    def pause(self):
        return self._run_cmd("pause")

    def stop(self):
        return self._run_cmd("stop")

    def ffwd(self, delta="30"):
        return self._run_cmd("ffwd", [delta])  # Fixed at 30 for now

    def rewind(self, delta="30"):
        return self._run_cmd("rewind", [delta])  # Fixed at 30 for now

    def seek(self, time):
        return self._run_cmd("seek", [str(time)])

    def skip(self):
        return self._run_cmd("skip")

    # Volume
    def volume_up(self, delta="15"):
        return self._run_cmd("volumeup", [delta])  # Fixed at 15 for now

    def volume_down(self, delta="15"):
        return self._run_cmd("volumedown", [delta])  # Fixed at 15 for now

    def mute(self):
        return self._run_cmd("volume", ["0"])

    # Miscellaneous
    def scan(self):
        output = self._run_cmd("scan", omit_device_name=True)
        # Expected output format: IPv4_addr - chromecast_name - Google Inc. Chromecast
        return re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3} - (.+?) - .*Chromecast", output)
