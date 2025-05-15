import time
from flask import Flask, jsonify, render_template
import pco
import getdropbox
import json
import os
import argparse
from enum import Enum
app = Flask(__name__)

# check if debug flag is present
parser = argparse.ArgumentParser(description="Check for debug mode flag.")
parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
args = parser.parse_args()
DEBUGMODE = args.debug

class ErrorType(Enum):
    INVALID_PCO_CREDENTIALS = "Invalid PlanningCenter credentials!"
    PCO_CONN_ERR = "Unable to connect to PlanningCenter!"
    INVALID_DB_CREDENTIALS = "Invalid Dropbox credentials!"
    DB_CONN_ERR = "Unable to connect to Dropbox!"
    
class ServerError:
    def __init__(self):
        self.errors = []
    def logError(self, error_type: ErrorType):
        print("Adding error " + error_type.name)
        if isinstance(error_type, ErrorType):
            if not error_type in self.errors:
                self.errors.append(error_type)
    def clearError(self, error_type: ErrorType):
        if isinstance(error_type, ErrorType):
            if error_type in self.errors:
                self.errors.remove(error_type)
    def __str__(self):
        if len(self.errors) == 0:
            return ""
        else:
            errorString = ""
            for error in self.errors:
                errorString += error.value + " "
            return errorString
    def hasError(self):
        return len(self.errors) > 0

serverError = ServerError()



def get_sections():
    """Reads section configuration from config.json."""
    with open("config.json") as f:
        data_obj = json.load(f)
    return data_obj.get("sections", [])

def get_image_url(name):
    """Return the URL to the image file if it exists in static/images."""
    if not name:
        return ""
    sanitized = name.lower().replace(" ", "_")
    for ext in [".jpg", ".png", ".JPG", ".JPEG",".jpeg",".PNG"]:
        image_path = os.path.join("static", "images", sanitized + ext)
        if os.path.exists(image_path):
            return f"/static/images/{sanitized}{ext}"
    return ""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def data():
    global serverError
    # get sections configuration
    sections = get_sections()
    try:
        with open("data.json") as f:
            raw_data = f.read()
            if not raw_data.strip():
                raise ValueError("data.json is empty")
            data = json.loads(raw_data)
    except Exception as e:
        data = {"sections":[], "serviceDateTime":""}
        
    if "error" in data:
        try:
            serverError.logError(ErrorType[data["error"]])
        except Exception as e:
            pass
    
    people = data.get("sections", [])
    # Add image URLs and persons name to each slot if available.
    for person in people:
        role = person.get("role", None)
        for section in sections:
            if section.get("role", "") == role:
                section["name"] = person.get("name", "")
                section["img"] = get_image_url(section.get("name", ""))
                break
            
    serviceDateTime = data.get("serviceDateTime", "")
    mdName = data.get("mdName", None)
            
    return jsonify({
        "success": True,
        "sections": sections,
        "serviceDateTime": serviceDateTime,
        "mdName": mdName,
        "error": str(serverError)
    })

if __name__ == "__main__":
    # Start the background thread before running the Flask app.
    pco.start_background_thread()
    getdropbox.start_background_thread()
    app.run(debug=DEBUGMODE, use_reloader=False)
