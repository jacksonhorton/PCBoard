from calendar import day_abbr
import sys
import datetime
from turtle import position
import time
from datetime import datetime
from datetime import date
from datetime import timedelta
from unicodedata import name
from urllib.parse import _NetlocResultMixinStr
from config2 import PCO_API_SECRET, PCO_APPLICATION_KEY

sys.path.append("/usr/local/lib/python3.9/site-packages")
sys.path.insert(0,'./')
sys.path.insert(0,'/usr/local/lib/python3.9/site-packages')
sys.path.append("..")
import pypco
import pytz

pco_update_list = []

FIRST_VOCALIST_SLOT = 1
MAX_NUM_VOCALISTS = 4
FIRST_HOST_SLOT = 6
MAX_NUM_HOSTS = 2

pco = pypco.PCO(PCO_APPLICATION_KEY, PCO_API_SECRET)
attachment_list = []
next_upcoming_plan = {}
service_types = {}
allowed_service_types = {'Overflow Weekend Experience'}
allowed_team_ids = {'1948319', '3611711'}
nowPlus = date.today() + timedelta(days=6)
now = nowPlus.strftime("%Y-%m-%dT%H:%M:%S%z")


def pco_json_mini(self):
    slot = self['slot']
    name = self['name']
    return {
        'slot': slot,
        'name': name,
        'timestamp': time.time()
    }

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
        raw_plans = pco.iterate('/services/v2/service_types/' + service_type['data']['id'] + '/plans', filter='future', order='sort_date', include='plan_times')
        for raw_plan in raw_plans:
            service_length = raw_plan['data']['attributes']['total_length']
            service_length = service_length + 300
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


def getTeamMembers(slot):
    upcoming_plan = getUpcomngPlan()
    assigned_team_members = pco.iterate('/services/v2/service_types/' + upcoming_plan['data']['relationships']['service_type']['data']['id'] + '/plans/' + upcoming_plan['data']['id'] + '/team_members',filter='confirmed')

    assigned_team_members = [assigned_member for assigned_member in assigned_team_members if assigned_member['data']['relationships']['team']['data']['id'] in allowed_team_ids]

    intNumber = 1
    vocals = {}
    for vocal_team_member in assigned_team_members:
        if slot == intNumber:
            # vocalString = str(intNumber) + '-' + vocal_team_member['data']['attributes']['name']
            name=vocal_team_member['data']['attributes']['name']
            newvocal={name:intNumber}
            vocals.update(newvocal)
            intNumber = intNumber + 1
        else:
            intNumber = intNumber + 1
        
    return vocals

def getTeam():
    upcoming_plan = getUpcomngPlan()
    
    assigned_team_members = pco.iterate('/services/v2/service_types/' + upcoming_plan['data']['relationships']['service_type']['data']['id'] + '/plans/' + upcoming_plan['data']['id'] + '/team_members',filter='confirmed')

    assigned_team_members = [assigned_member for assigned_member in assigned_team_members if assigned_member['data']['relationships']['team']['data']['id'] in allowed_team_ids]
    
    slots = []
    vocals = []
    hosts = []
    for vocal_team_member in assigned_team_members:
            # vocalString = str(intNumber) + '-' + vocal_team_member['data']['attributes']['name']
            name=vocal_team_member['data']['attributes']['name']
            # print(name)
            pcoPosition = vocal_team_member['data']['attributes']['team_position_name']
            # print(pcoPosition)
            slot_number = False
            if pcoPosition == "Vocalist":
                vocals.append(name)
            elif pcoPosition == "Hosting":
                hosts.append(name)
            # mic_number = [int(s) for s in str.split(pcoPosition) if s.isdigit()]
            # if slot_number:
            #     newslot={'slot':slot_number, 'name':name, 'position': pcoPosition}
            #     print(newslot)
            #     slots.append(newslot)
            #     if newslot not in pco_update_list:
            #         pco_update_list.append(newslot)
                    
    # sort everyone and assign slots
    vocals = sorted(vocals)
    hosts = sorted(hosts)
    
    for index, name in enumerate(vocals):
        if (index < MAX_NUM_VOCALISTS):
            newslot={'slot':index+FIRST_VOCALIST_SLOT, 'name':name, 'position': "Vocalist"}
            slots.append(newslot)
    for index, name in enumerate(hosts):
        if (index < MAX_NUM_HOSTS):
            newslot={'slot':index+FIRST_HOST_SLOT, 'name':name, 'position': "Host"}
            slots.append(newslot)

    return slots

