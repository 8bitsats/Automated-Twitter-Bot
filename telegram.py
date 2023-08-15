<<<<<<< HEAD
import telegram
# from telegram.ext.chatbot import Chat
=======
import requests
import os
>>>>>>> 7cf8c6c68249385b68290ad0a6555da376d7fcb7

def download_media(channel_id, media_file_url):
    """Downloads a media file from a Telegram channel.

    Args:
        channel_id: The ID of the Telegram channel.
        media_file_url: The URL of the media file to download.
    """

    filename = media_file_url.split("/")[-1]
    response = requests.get(media_file_url, stream=True)

    if response.status_code == 200:
        with open(os.path.join("Media_Files", filename), "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)

    else:
        print("Error downloading media file:", response.status_code)

if __name__ == "__main__":
    channel_id = "Nature"
    media_file_url = "https://t.me/Nature/1"

    download_media(channel_id, media_file_url)
