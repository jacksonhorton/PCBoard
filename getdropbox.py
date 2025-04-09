import threading
import os
import sys
import dropbox
from dotenv import load_dotenv
from pathlib import Path
from time import sleep

import hashlib
import six


# From .env
load_dotenv()
DB_OAUTH2_REFRESH_TOKEN = os.environ["DB_OAUTH2_REFRESH_TOKEN"] 
DB_APP_KEY = os.environ["DB_APP_KEY"] 
DB_APP_SECRET = os.environ["DB_APP_SECRET"]

# Constants
imagesDirectory = "static/images"


def start_background_thread():
    """Starts the background thread for fetching data."""
    setupImageDirectory()
    thread = threading.Thread(target=fetch_data, daemon=True)
    thread.start()

def fetch_data():
    while True:
        try:
            getFiles()
        except Exception as e:
            print(f"Error fetching dropbox files: {e}")
        sleep(600)

def setupImageDirectory():
    # Ensure the directory exists
    Path(imagesDirectory).mkdir(parents=True, exist_ok=True)

class DropboxContentHasher(object):
    """
    Computes a hash using the same algorithm that the Dropbox API uses for the
    the "content_hash" metadata field.
    The digest() method returns a raw binary representation of the hash.  The
    hexdigest() convenience method returns a hexadecimal-encoded version, which
    is what the "content_hash" metadata field uses.
    This class has the same interface as the hashers in the standard 'hashlib'
    package.
    Example:
        hasher = DropboxContentHasher()
        with open('some-file', 'rb') as f:
            while True:
                chunk = f.read(1024)  # or whatever chunk size you want
                if len(chunk) == 0:
                    break
                hasher.update(chunk)
        print(hasher.hexdigest())
    """

    BLOCK_SIZE = 4 * 1024 * 1024

    def __init__(self):
        self._overall_hasher = hashlib.sha256()
        self._block_hasher = hashlib.sha256()
        self._block_pos = 0

        self.digest_size = self._overall_hasher.digest_size
        # hashlib classes also define 'block_size', but I don't know how people use that value

    def update(self, new_data):
        if self._overall_hasher is None:
            raise AssertionError(
                "can't use this object anymore; you already called digest()")

        assert isinstance(new_data, six.binary_type), (
            "Expecting a byte string, got {!r}".format(new_data))

        new_data_pos = 0
        while new_data_pos < len(new_data):
            if self._block_pos == self.BLOCK_SIZE:
                self._overall_hasher.update(self._block_hasher.digest())
                self._block_hasher = hashlib.sha256()
                self._block_pos = 0

            space_in_block = self.BLOCK_SIZE - self._block_pos
            part = new_data[new_data_pos:(new_data_pos+space_in_block)]
            self._block_hasher.update(part)

            self._block_pos += len(part)
            new_data_pos += len(part)

    def _finish(self):
        if self._overall_hasher is None:
            raise AssertionError(
                "can't use this object anymore; you already called digest() or hexdigest()")

        if self._block_pos > 0:
            self._overall_hasher.update(self._block_hasher.digest())
            self._block_hasher = None
        h = self._overall_hasher
        self._overall_hasher = None  # Make sure we can't use this object anymore.
        return h

    def digest(self):
        return self._finish().digest()

    def hexdigest(self):
        return self._finish().hexdigest()

    def copy(self):
        c = DropboxContentHasher.__new__(DropboxContentHasher)
        c._overall_hasher = self._overall_hasher.copy()
        c._block_hasher = self._block_hasher.copy()
        c._block_pos = self._block_pos
        return c

def filehash(fn):
    hasher = DropboxContentHasher()
    with open(fn, 'rb') as f:
        while True:
            chunk = f.read(1024)  # or whatever chunk size you want
            if len(chunk) == 0:
                break
            hasher.update(chunk)
    return hasher.hexdigest()

def getFiles():
    # Authenticate with Dropbox
    print('Downloading images from Dropbox...')
    print('Local images folder is ' + imagesDirectory)
    dbx = dropbox.Dropbox(
                app_key = DB_APP_KEY,
                app_secret = DB_APP_SECRET,
                oauth2_refresh_token = DB_OAUTH2_REFRESH_TOKEN
    )
    for entry in dbx.files_list_folder('').entries:
        localfile = Path(imagesDirectory + '/' + entry.name)
        if localfile.is_file():
            localfilehash = filehash(localfile)
            if localfilehash == entry.content_hash:
                # print(entry.name + ' already exists. No update needed')
                continue
            else:
                print(entry.name + ' has been updated. Downloading update.')
                newPath = imagesDirectory + '/' + entry.name
                currentPath = '/' + entry.name
                dbx.files_download_to_file(newPath,currentPath)
        else:
            print(entry.name + ' does not exist. Downloading file')
            newPath = imagesDirectory + '/' + entry.name
            currentPath = '/' + entry.name
            dbx.files_download_to_file(newPath,currentPath)
    
if __name__ == "__main__":
    while True:
        getFiles()
        sleep(10)