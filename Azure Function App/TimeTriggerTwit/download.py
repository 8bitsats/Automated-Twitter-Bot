import os
import logging
import requests
import regex as re
from bs4 import BeautifulSoup
from datetime import datetime
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import BlobType


def download_video(url, channel, message_id,container_name):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Search for the video tag and extract the 'src' attribute
    video_url = soup.find('video')['src']
    video_response = requests.get(video_url, stream=True)
    video_response.raise_for_status()

    # Create a BlobClient for the file in the container
    filename = f'{channel}-{message_id}.mp4'
    blob_container_client = blob_service_client.get_container_client(container_name)
    blob_client = blob_container_client.get_blob_client(filename)

    # Upload the file's content to Azure Blob Storage
    if not blob_client.exists():
        blob_client.upload_blob(video_response.content)

    return filename
 

def download_image(url, channel, message_id, container_name):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    # Find the anchor tag with the class "tgme_widget_message_photo_wrap" and extract the background-image URL from its style attribute
    image_tag = soup.find('a', class_='tgme_widget_message_photo_wrap')
    image_url = image_tag['style'].split('url(')[1].split(')')[0].strip("'")

    img_response = requests.get(image_url, stream=True)
    img_response.raise_for_status()

    # Create a BlobClient for the file in the container
    filename = f'{channel}-{message_id}.jpg'
    blob_container_client = blob_service_client.get_container_client(container_name)
    blob_client = blob_container_client.get_blob_client(filename)

    # Upload the file's content to Azure Blob Storage
    if not blob_client.exists():
        blob_client.upload_blob(img_response.content)
  
    return filename


def get_caption(url,log_values):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    # Find the div with the class "tgme_widget_message_text" 
    if bool(soup.find('div', class_='tgme_widget_message_text')) == True:
        message_div = soup.find('div', class_='tgme_widget_message_text')
        caption = list(message_div.stripped_strings)[0]  # This splits the content based on the presence of tags
    else:
        caption = "#Nature is just amazing 🌎"
    
    log_values.append(caption)
    return caption


def post_not_found(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    error = soup.find('div', class_="tgme_widget_message_error")
    
    if error and error.text == "Post not found":
        # print("Page not found")
        return True
    else:
        return False


