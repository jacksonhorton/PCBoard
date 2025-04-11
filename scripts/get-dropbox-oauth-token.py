import requests
import dropbox
from dropbox.oauth import DropboxOAuth2FlowNoRedirect

'''
This script is a helper to generate an OAUTH Refresh Token to
be used by getdropbox.py to fetch images from your dropbox app.
Here are the instructions:

  Create a Dropbox app:
    Go to https://www.dropbox.com/developers/app
    Create App.
        Scoped Access
        App Folder (You can use Full Dropbox if you know what you're doing)
        Name it something like "Micboard"
    It will show the app it just created. Copy the App Key, App Secret into
    the script below, then hit the "Generate Access Token" button and copy
    the token into the script below.
    Go to the Permissions tab and check yes for files.metadata.read and
    files.content.read. Then hit "Submit".
    Now run this script and follow instructions on the command line.
'''

APP_KEY=""
APP_SECRET=""

GENERATED_ACCESS_TOKEN = ""


# Initialize the OAuth2 flow without a redirect URI (for offline use)
auth_flow = DropboxOAuth2FlowNoRedirect(
    consumer_key=APP_KEY,
    consumer_secret=APP_SECRET,
    token_access_type="offline"  # This ensures a refresh token is returned
)

# Generate the authorization URL
authorize_url = auth_flow.start()
print("1. Go to this URL:", authorize_url)
print("2. Click 'Allow' (you might need to log in first).")
print("3. Copy the authorization code and paste it below.")


# Paste the authorization code you got from the browser
auth_code = input("Enter the authorization code: ")

# Exchange the code for tokens
try:
    oauth_result = auth_flow.finish(auth_code)
    print("Put this token in the .env file as DB_OAUTH2_REFRESH_TOKEN:")
    print("OAUTH2 Refresh Token:", oauth_result.refresh_token)
except Exception as e:
    print("Error:", e)