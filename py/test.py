import sys

sys.path.append("/usr/local/lib/python3.9/site-packages")
sys.path.append('.')
import dropbox

from dotenv import dotvalues

ENV = dotvalues()

# ...


# Authenticate with Dropbox
print('Downloading images from Dropbox...')
dbx = dropbox.Dropbox(app_key = key, app_secret = secret, oauth2_refresh_token = access_token)

for entry in dbx.files_list_folder('').entries:
    print(entry)