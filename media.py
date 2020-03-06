import os
import re
import uuid

import config


class Media():
    def __init__(self, f):
        self.path = f
        self.parent_dirs = os.path.dirname(f).split("/")
        self.uuid = str(uuid.uuid4())
        self.title = self.find_title()
        self.season = self.find_season()
        self.episode = self.find_episode()
        self.cover_art = self.find_cover_art()
        self.history = {}

    def _remove_text_in_brackets(self, text):
        """Remove any text inside [] or ()"""
        return re.sub(r"\[.*?\]|\(.*?\)", "", text).strip()

    def _remove_junk_words(self, text):
        for w in config.JUNK_WORDS:
            return re.sub(w, "", text, flags=re.IGNORECASE)

    def _symbols_to_spaces(self, text):
        # @todo: I shouldn't remove dashes if the format is Show - Episode#
        return re.sub(r"[\._-]", " ", text)

    def find_title(self):
        # basename minus file extension
        return os.path.splitext(os.path.basename(self.path))[0]
        # filename = self.path.split("/")[-1]
        # s = self._remove_file_extension(filename)
        # # s = self._remove_junk_words(s)
        # s = self._remove_text_in_brackets(s)
        # s = self._symbols_to_spaces(s)
        # s = s.lstrip().strip()  # Remove leading and trailing spaces
        # return ' '.join(s.split())  # Replace 2+ spaces with single space

    def find_season(self):
        season = re.findall(r"S(\d{2})", self.path, flags=re.IGNORECASE)
        if season:
            return season[-1]  # The last instance is usually correct
        return ""

    def find_episode(self):
        episode = re.findall(r"E(\d{2,3})", self.path, flags=re.IGNORECASE)
        if episode:
            return episode[-1]  # The last instance is usually correct
        return ""

    def find_cover_art(self):
        return ""

    def json(self):
        return {"path": self.path,
                "parent_dirs": self.parent_dirs,
                "title": self.title,
                "season": self.season,
                "episode": self.episode,
                "cover_art": self.cover_art,
                "history": self.history,
                "uuid": self.uuid}
