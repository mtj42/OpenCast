import os
import re
import json
import time
import string
import random
import subprocess

import config
from media import Media

from IPython import embed


def build_media_library():
    media = []
    t0 = time.time()
    for root, dir_names, file_names in os.walk(config.MEDIA_BASE_DIR):
        for f in file_names:
            if os.path.splitext(f)[1] in config.SUPPORTED_MEDIA_FORMATS:
                m = Media(os.path.join(root, f))
                media.append(m.json())
    if not media:
        return {"warning": "No media found in {}".format(config.MEDIA_BASE_DIR)}
    with open(config.MEDIA_JSON, "w") as f:
        f.write(json.dumps(media, indent=4))
    elapsed = round(time.time() - t0, 2)
    return {"success": "{} entries written to {} in {} seconds"
                       .format(len(media), config.MEDIA_JSON, elapsed)}


def search_media(key, query):
    with open("cache/media.json", "r") as f:
        media = json.loads(f.read())
        result = list(filter(lambda m: m[key] == query, media))
        if not result:
            print("[Warning]: search_media({}, {}) returned 0 results.".format(key, query))
        return result


def pretty_filename(name):
    # @todo: spaghetti code
    junk_words = ["DVDRip", "x264", "264", "BluRay", "x265", "265", "XviD",
                  "BDRip", "HDTV", "720p", "1080p", "REPACK", "Uncensored",
                  "HEVC"] + config.SUPPORTED_MEDIA_FORMATS
    for w in junk_words:
        w_re = w + ".*?$"
        name = re.sub(w_re, "", name, flags=re.IGNORECASE)  # Remove junk words
    name = re.sub(r"[-_\.]", " ", name)  # Pretty spaces
    name = re.sub(r"\[HorribleSubs\]", "", name)
    name = name.strip()
    return name


def prettify_dir_name(name):
    # @todo: Not relevant yet, but this may need to be updated to support files rather than folders
    junk_words = ["DVDRip", "x264", "264", "BluRay", "x265", "265", "XviD", "BDRip", "HDTV", "720p", "1080p", "REPACK", "Uncensored",
            "HEVC", "2009", "2018"]
    for w in junk_words:
        w_re = w + ".*?$" 
        name = re.sub(w_re, "", name, flags=re.IGNORECASE) # Remove junk words
        # Format is usually "Movie.Or.Show.Name" optionally followed by
        # "S01-S09", always followed by "Junk.Words.Just-All.Over-the.Place" So
        # just strip it from the first occurence of junk to the end of the link
    name = re.sub("[-_\.]", " ", name) # Pretty spaces
    name = name.strip()
    name = re.sub("\[HorribleSubs\] ", "", name)
    # Pretty S01 or S01 S19 --> (Season 1) or (Season 1-19)
    # @todo: Improve this
    # m = re.search("S(\d{2})( S(\d{2}))?", name, flags=re.IGNORECASE)
    # if m:
    #     groups = m.groups() # G0 = "01", G1 = " S19", G2 = "19"
    #     if groups[0] and not groups[1]:
    #         name = name.replace("S" + groups[0], "(Season {})".format(groups[0]))
    #     else:
    #         name = name.replace("S" + groups[0] + groups[1], "(Seasons {}-{})".format(groups[0], groups[2]))

    return name


def process_mkv(mkv_filepath):
    """Extract subtitles from an mkv file."""
    # @todo: security
    out = subprocess.check_output(["mkvmerge","-i",mkv_filepath]).decode("utf-8")
    m = re.search("Track ID (\d): subtitles(.*\n)?", out)
    track_id = m.group(1)
    if "substationalpha" in m.group(2).lower():
        print("Subtitle format detected: SubStationAlpha")
        rand_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        tmp_file = "/tmp/catt_subtitle_{}".format(rand_name)
        # Slow af if over the network, but fast if local
        subprocess.run(["mkvextract", "tracks", mkv_filepath,
                        "{}:{}.ass".format(track_id, tmp_file)])
        #print("Extracted to {}.ass".format(tmp_file))
        subprocess.run(["ffmpeg", "-i", "{}.ass".format(tmp_file),
                        "{}.vtt".format(tmp_file)])
        #print("Converted to WebVTT: {}.vtt".format(tmp_file))
        return "{}.vtt".format(tmp_file)
    return ""
