import requests
import json
import logging
from pathlib import Path

logging.getLogger().setLevel(logging.INFO)

class Forvo:
    BASE_URL = "https://apifree.forvo.com"

    def __init__(self, api_key: str, download_path: str):
        self.api_key = api_key
        self.download_path = download_path
        Path(self.download_path).mkdir(parents=True, exist_ok=True)

    
    def _request(self, **params):
        components = [f"key/{self.api_key}"]

        for key, value in params.items():
            components.append(f"{key}/{value}")

        full_path = f"{self.BASE_URL}/{'/'.join(components)}"
        return requests.get(full_path)


    def pronunciations(self, language: str, word: str, **extra):
        r = self._request(format="json", action="word-pronunciations",
                          word=word, language="ru", **extra)
        return r.json()


    def download_audio(self, language: str, word: str, **extra):
        audio_file = Path(self.download_path) / f"{word}.mp3"

        if audio_file.exists():
            logging.info(f"Audio for word '{word}' already exists!")
            return audio_file

        r = self._request(format="json", action="word-pronunciations",
                          word=word, language=language, **extra)

        if r.status_code != 200:
            logging.error(f"Failed to retrieve pronunciations JSON for '{word}'! Status code: {r.status_code}")
            logging.error(f"Content: {r}")
            return None

        r_json = r.json()

        try:

            most_votes = max(r_json["items"],
                                key=lambda item: item["num_positive_votes"])
            r = requests.get(most_votes['pathmp3'])
        except Exception as err:
            logging.error(f"Encountered error when attempting to parse returned JSON: {err}")
            return None


        # If the request was successful, download and save the file
        if r.status_code == 200:
            with open(audio_file, 'wb') as f:
                f.write(r.content)
            logging.info(f"Downloaded audio for word '{word}'")
            return audio_file
        else:
            logging.error(f"Failed to download audio for word '{word}'. "
                          f"Status code returned: {r.status_code}")
            return None
