import requests
import re
from bs4 import BeautifulSoup

def get_media_from_telegram_link(telegram_link):
    # Fetch the page content
    response = requests.get(telegram_link)
    response.raise_for_status()

    html_content = response.text
    # with open("html_file.html", "w") as f:
    #     f.write(html_content)
    # print(html_content)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Get media and caption elements
    og_media_url = soup.find("meta", property="og:image")
    og_caption = soup.find("meta", property="og:description")
    twitter_media_url = soup.find("meta", property="twitter:image")
    twitter_caption = soup.find("meta", property="twitter:description")

    # Get media url
    if og_media_url is not None:
        media_url = og_media_url["content"]
    elif twitter_media_url is not None:
        media_url = twitter_media_url["content"]

    else:
        print("Could not find the expected image element. The structure of the page might have changed.")
        return
    
    # get the caption
    if og_caption is not None:
        text_caption = og_caption["content"].split("\n")[0]
    elif twitter_caption is not None:
        text_caption = twitter_caption["content"].split("\n")[0]
    else:
        text_caption = "#Nature is amazing 🌎"

    match = re.search(r"International Nature channel. Discover Earth with us!", text_caption)
    if not match:
        # Download the media
        media_response = requests.get(media_url, stream=True)
        media_response.raise_for_status()


        # Save the media to a local file
        split_link = telegram_link.split("/")[-2:]
        if media_url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
            filename = "_".join(split_link) + "." + media_url.split(".")[-1]
        else:
            filename = "_".join(split_link)
        with open(filename, 'wb') as file:
            for chunk in media_response.iter_content(chunk_size=8192):
                file.write(chunk)
        print("File name: ", filename)
        print(text_caption)
    else:
        pass


# Test with your Telegram link
get_media_from_telegram_link("https://t.me/Nature/139")
# https://t.me/Nature/5611