from requests_oauthlib import OAuth1Session
import os
import json
import webbrowser
from selenium import webdriver
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


consumer_key = str(os.getenv('CONSUMER_KEY'))
consumer_secret = str(os.getenv('API_SECRET_KEY'))
access_token = str(os.getenv('ACCESS_TOKEN'))
access_token_secret = str(os.getenv('ACCESS_TOKEN_SECRET'))

payload = {"text": "Data is always ready to perform, 24/7! 💪. You like it or not"}

# Get request token
request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

try:
    fetch_response = oauth.fetch_request_token(request_token_url)
except ValueError:
    print(
        "There may have been an issue with the consumer_key or consumer_secret you entered."
    )

resource_owner_key = fetch_response.get("oauth_token")
resource_owner_secret = fetch_response.get("oauth_token_secret")


# Get authorization
base_authorization_url = "https://api.twitter.com/oauth/authorize"
authorization_url = oauth.authorization_url(base_authorization_url)


browser = webdriver.Firefox(executable_path='/geckodriver')
browser.get(authorization_url)
# webbrowser.open(authorization_url)
element= browser.find_element(by="id", value="allow")
element.click()
verifier = input("Paste the PIN here: ")


# Get the access token
access_token_url = "https://api.twitter.com/oauth/access_token"
oauth = OAuth1Session(
    consumer_key,
    client_secret=consumer_secret,
    resource_owner_key=resource_owner_key,
    resource_owner_secret=resource_owner_secret,
    verifier=verifier,
)
oauth_tokens = oauth.fetch_access_token(access_token_url)

# access_token = oauth_tokens["oauth_token"]
# access_token_secret = oauth_tokens["oauth_token_secret"]

# Make the request
oauth = OAuth1Session(
    consumer_key,
    client_secret=consumer_secret,
    resource_owner_key=access_token,
    resource_owner_secret=access_token_secret,
)

# Making the request
response = oauth.post(
    "https://api.twitter.com/2/tweets",
    json=payload,
)

if response.status_code != 201:
    raise Exception(
        "Request returned an error: {} {}".format(response.status_code, response.text)
    )

print("Response code: {}".format(response.status_code))

# # Saving the response as JSON
# json_response = response.json()
# print(json.dumps(json_response, indent=4, sort_keys=True))