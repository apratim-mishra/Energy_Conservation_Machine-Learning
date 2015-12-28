import requests
import datetime
import json
import random

# python ~/smart_home_app/client/client_simulator.py

# see example : https://realpython.com/blog/python/api-integration-in-python/



home_id = "homeid1"

device_list = ("d1",  "d2", "d2", "d3", "d4")
curr_time = datetime.datetime.now()
curr_time_str = curr_ime.isoformat()

print(curr_time_str)
curr_time_minute = curr_time.minute

task = {"home_id": home_id,
        "timestamp_hour": curr_time_str,
        "device_visibility": {
            "d1": {"0": 1, "1": 1},
            "d2": {"0": 1, "1": 0},
            "d3": {"0": 0, "1": 1}
        }
        }


url = "http://localhost:8000/smart_home_app/?"


# simulate for the whole week, for each hour
for day in range(0, 6):
    for hour in range(0, 23):
        for minute in range(0, 59):
            curr_time = curr_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            home_doc_map = {}
            device_visibility_doc_map = {}

            for device_num in range(0, len(device_list) - 1):
                # Go thru all the devices and randomly assign some devices as visible
                if random.random() >= 0.5:
                    device = device_list[device_num]
                    minute_value_map = {}
                    minute_value_map[minute] = "1"
                    device_visibility_doc_map[device] = minute_value_map

            home_doc_map["home_id"] = home_id
            home_doc_map["timestamp_hour"] = curr_time.isoformat()
            home_doc_map["device_visibility"] = device_visibility_doc_map
            # print(home_doc_map)
            # convert a map to a json doc
            home_doc_json = json.dumps(home_doc_map)
            # print(home_doc_json)
            if len(device_visibility_doc_map) > 0:
                # we have some device visible, so post it to the server.
                resp = requests.post(url, data=home_doc_json)
                print(resp)
                if resp.status_code != 201 and resp.status_code != 200:
                   raise ApiError('POST /tasks/ {}'.format(resp.status_code))
                # print('Created task. ID: {}'.format(resp.json()["id"]))


#resp = requests.post(url, data=task)
#if resp.status_code != 201:
#    raise ApiError('POST /tasks/ {}'.format(resp.status_code))
#print('Created task. ID: {}'.format(resp.json()["id"]))


