import threading
import time
import os
from dotenv import load_dotenv
from calendar import day_abbr
import sys
import json
import datetime
from turtle import position
import time
from datetime import datetime
from datetime import date
from datetime import timedelta
from unicodedata import name

sys.path.append("/usr/local/lib/python3.9/site-packages")
sys.path.insert(0,'./')
sys.path.insert(0,'/usr/local/lib/python3.9/site-packages')
sys.path.append("..")
import pypco
import pytz


# From .env
load_dotenv()
PCO_APPLICATION_KEY = os.environ["PCO_APPLICATION_KEY"] 
PCO_API_SECRET = os.environ["PCO_API_SECRET"]

# Constants
FIRST_VOCALIST_SLOT = 1
MAX_NUM_VOCALISTS = 3
FIRST_HOST_SLOT = 4
MAX_NUM_HOSTS = 2

# PCO Stuff
pco = pypco.PCO(PCO_APPLICATION_KEY, PCO_API_SECRET)
attachment_list = []
next_upcoming_plan = {}
service_types = {}
allowed_service_types = {'Overflow Weekend Experience'}
allowed_team_ids = {'1948319', '3611711'}
nowPlus = date.today() + timedelta(days=6)
now = nowPlus.strftime("%Y-%m-%dT%H:%M:%S%z")


    
def fetch_data():
    """Background function that fetches data from Planning Center online."""
    while True:
        try:
            print("Fetching data from Planning Center online...")
            upcoming_plan = getUpcomngPlan()
            sections = getTeam(upcoming_plan)
            serviceDateTime = upcoming_plan['data']['attributes']['sort_date']
            update_data_file(sections=sections, serviceDateTime=serviceDateTime)
            
        except Exception as e:
            print(f"Error fetching data: {e}")

        time.sleep(600)
        
def findMDName(data):
    for item in data:
        if item.get("role") == "MD":
            return item.get("name")
    return None
            
def getServiceTypes():
    service_types = pco.iterate('/services/v2/service_types')
    service_types = [service_type for service_type in service_types if service_type['data']['attributes']['name'] in allowed_service_types]
    return service_types

def getUpcomngPlan():
    utc = pytz.UTC
    today = utc.localize(datetime.now())
    service_types = getServiceTypes()
    next_upcoming_plan = {}
    for service_type in service_types:
        raw_plans = pco.iterate('/services/v2/service_types/' + service_type['data']['id'] + '/plans', per_page=50, order='-sort_date', include='plan_times')
        for raw_plan in raw_plans:
            # print(f"raw plan:  {raw_plan['data']['attributes']['sort_date']}")
            service_length = raw_plan['data']['attributes']['total_length']
            # service_length = service_length + 300
            service_length = service_length + 50000
            sort_date =  datetime.strptime(raw_plan['data']['attributes']['sort_date'],'%Y-%m-%dT%H:%M:%S%z')
            end_date = sort_date + timedelta(seconds=service_length)
            if next_upcoming_plan:
                next_date = datetime.strptime(next_upcoming_plan['data']['attributes']['sort_date'], '%Y-%m-%dT%H:%M:%S%z')
                if sort_date < next_date:
                    if end_date > today:
                        next_upcoming_plan = raw_plan
            else:
                if end_date > today:
                    next_upcoming_plan = raw_plan
    return next_upcoming_plan

def getTeam(upcoming_plan):
    print("TODAY IS: " + upcoming_plan['data']['attributes']['sort_date'])
    assigned_team_members = pco.iterate('/services/v2/service_types/' + upcoming_plan['data']['relationships']['service_type']['data']['id'] + '/plans/' + upcoming_plan['data']['id'] + '/team_members',filter='confirmed')

    assigned_team_members = [assigned_member for assigned_member in assigned_team_members if assigned_member['data']['relationships']['team']['data']['id'] in allowed_team_ids]
    # print(assigned_team_members)
    
    slots = []
    vocals = []
    hosts = []
    for team_member in assigned_team_members:
            # vocalString = str(intNumber) + '-' + vocal_team_member['data']['attributes']['name']
            name=team_member['data']['attributes']['name']
            # print(name)
            pcoPosition = team_member['data']['attributes']['team_position_name']
            # print(pcoPosition)
            slot_number = False
            if pcoPosition == "Vocalist":
                vocals.append(name)
            elif pcoPosition == "Host":
                hosts.append(name)
            else:
                newslot={'role': pcoPosition, 'name':name}
                slots.append(newslot)

                    
    # sort everyone and assign slots
    vocals = sorted(vocals)
    hosts = sorted(hosts)
    
    for index, name in enumerate(vocals):
        if (index < MAX_NUM_VOCALISTS):
            newslot={'role':f"Vocal {index+FIRST_VOCALIST_SLOT}", 'name':name}
            slots.append(newslot)
    for index, name in enumerate(hosts):
        if (index < MAX_NUM_HOSTS):
            newslot={'role':f"Host {index+FIRST_VOCALIST_SLOT}", 'name':name}
            slots.append(newslot)

    return slots

def update_data_file(sections=[], serviceDateTime=""):
    # try to format service datetime
    formattedServiceDateTime = ""
    try:
        dt = datetime.strptime(serviceDateTime, "%Y-%m-%dT%H:%M:%SZ")
        formattedServiceDateTime = dt.strftime("%A, %B %d at %-I:%M %p")
    except:
        print("Failed to format incoming serviceDateTime. This can be ignored.")
    
    data = {}
    data["sections"] = sections
    data["serviceDateTime"] = formattedServiceDateTime
    mdName =  findMDName(sections)
    if mdName:
        data["mdName"] = mdName
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

def start_background_thread():
    """Starts the background thread for fetching data."""
    thread = threading.Thread(target=fetch_data, daemon=True)
    thread.start()

if __name__ == "__main__":
    fetch_data()