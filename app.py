import time
from flask import Flask, jsonify, render_template
import pco
import getdropbox
import json
import os
import argparse

app = Flask(__name__)

# check if debug flag is present
parser = argparse.ArgumentParser(description="Check for debug mode flag.")
parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
args = parser.parse_args()
DEBUGMODE = args.debug


def fetch_data():
    """Background thread function to fetch data periodically."""
    while True:
        try:
            # Replace this with your code to fetch data from Planning Center online.
            print("Fetching data from Planning Center online...")
            # For example, you might update a JSON file or shared variable here.
            time.sleep(60)  # Wait for 60 seconds before fetching again.
        except Exception as e:
            print(f"Error fetching data: {e}")
            time.sleep(60)

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
    for ext in [".jpg", ".png"]:
        image_path = os.path.join("static", "images", sanitized + ext)
        if os.path.exists(image_path):
            return f"/static/images/{sanitized}{ext}"
    return ""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def data():
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
        "mdName": mdName
    })

if __name__ == "__main__":
    # Start the background thread before running the Flask app.
    pco.start_background_thread()
    getdropbox.start_background_thread()
    if DEBUGMODE == True:
        app.run(debug=True, use_reloader=False)
    else:
        app.run(debug=False, use_reloader=False)
