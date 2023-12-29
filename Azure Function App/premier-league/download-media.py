import requests
from datetime import datetime
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor


#************************************ VARIABLES ****************************************************

channel_name = "premier_league_football_news"
# account_name = re.search("AccountName=(.*?);", connection_string).group(1)
telegram_url = f"https://t.me/{channel_name}"


def find_media(url, message_id):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    response_primary = requests.get(url=f"{telegram_url}/{message_id}?embed=1&mode=tme")
    soup_primary = BeautifulSoup(response_primary.content, "html.parser")

    if soup_primary.find('div', class_='tgme_widget_message_grouped_wrap'):
        photo_wrap_classes = soup_primary.find_all('a', class_='tgme_widget_message_photo_wrap')
        print(f"Grouped media with {len(photo_wrap_classes)} images")

        for i in range(0, len(photo_wrap_classes)):
            download_url = f"https://t.me/{channel_name}/{message_id+i}?embed=1&mode=tme&single=1"
            download_image(url=download_url, message_id=message_id+i)

    elif soup_primary.find('a', class_='tgme_widget_message_photo_wrap') and not soup_primary.find('div', class_='tgme_widget_message_grouped_wrap'):
        download_url = f"https://t.me/{channel_name}/{message_id}?embed=1&mode=tme"
        download_image(url=download_url, message_id=message_id)


def download_image(url, message_id):
    response_sec = requests.get(url)
    soup_sec = BeautifulSoup(response_sec.content, "html.parser")

    if soup_sec.find('div', class_="tgme_widget_message_error"):
        print("No media")
        return

    image_tag = soup_sec.find('a', class_='tgme_widget_message_photo_wrap')
    image_url = image_tag['style'].split('url(')[1].split(')')[0].strip("'")
    filename = f'{channel_name}-{message_id}.jpg'

    with requests.get(image_url, stream=True) as response:
        with open(filename, 'wb') as img_file:
            for chunk in response.iter_content(chunk_size=8192):
                img_file.write(chunk)


find_media(url=telegram_url, message_id=23386)