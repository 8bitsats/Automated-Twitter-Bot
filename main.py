from auth import authenticate_openai
from auth import authenticate_twitter

if __name__ == "__main__":
    # Authenticate with Twitter and OpenAI
    twitter_api = authenticate_twitter()
    openai_authenticated = authenticate_openai()

    # Continue with the rest of the code if both authentications are successful
    if twitter_api and openai_authenticated:
        # Your code for generating tweets and interactions here
        pass
    else:
        print("Authentication failed. Please check your API keys and tokens.")