import requests
import datetime
import json
import random

# python ~/smart_home_app/client/client_simulator.py

# see example : https://realpython.com/blog/python/api-integration-in-python/



home_id = "homeid1"

device_list = ("1",  "2", "3", "4", "5", "6", "7", "8", "9", "10")

curr_time = datetime.datetime.now()
curr_time_str = curr_time.isoformat()
# sample document structure
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
for day in range(0, 7):  # 0..6
    for hour in range(0, 24):  # 0..23
        home_doc_map = {}
        device_visibility_doc_map = {}
        # randomly pick number of device clusters for this hour
        clusters = random.randint(0, len(device_list)-1)
        for cluster_number in range(0, clusters):
            minute_start = random.randint(0, 30)
            minute_end = random.randint(minute_start, 59)
            # pick visible devices for this hour
            for device_num in range(0, len(device_list) - 1):
                # Go thru all the devices and randomly assign some devices as visible
                if random.random() >= 0.5:
                    device = device_list[device_num]
                    minute_value_map = {}

                    for minute in range(minute_start, minute_end+1):
                        minute_value_map[minute] = "1"
                        device_visibility_doc_map[device] = minute_value_map

                    future_time = curr_time.replace(hour=hour, minute=minute, second=0, microsecond=0) \
                                  + datetime.timedelta(days=day)
                    home_doc_map["home_id"] = home_id
                    home_doc_map["timestamp_hour"] = future_time.isoformat()
                    home_doc_map["device_visibility"] = device_visibility_doc_map
                    home_doc_json = json.dumps(home_doc_map)
                    print(home_doc_json)
                    if len(device_visibility_doc_map) > 0:
                        # test = 1
                        # we have some device visible, so post it to the server.
                        resp = requests.post(url, data=home_doc_json)
                        # print(resp)
                        if resp.status_code != 201 and resp.status_code != 200:
                            raise ApiError('POST /tasks/ {}'.format(resp.status_code))
                        # print('Created task. ID: {}'.format(resp.json()["id"]))
