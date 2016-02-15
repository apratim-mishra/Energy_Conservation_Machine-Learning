import os
import requests
import datetime
import json
import random
import nmap

# in ubuntu: sudo apt-get install nmap
#           sudo python -m easy_install python-nmap
#
# in mac: sudo easy_install python-nmap
# python client_home1.py 
# ['192.168.1.1', '192.168.1.104', '192.168.1.106', '192.168.1.107', '192.168.1.109', '192.168.1.118', '192.168.1.119', '192.168.1.145', '192.168.1.146']


nm = nmap.PortScanner()
home_id = "homeid1"
network_addr_to_scan = "192.168.1.1/24"
url = "http://localhost:8000/smart_home_app/?"

# sample document structure
#task = {"home_id": home_id,
#        "timestamp_hour": curr_time_str,
#        "device_visibility": {
#            "d1": {"0": 1, "1": 1},
#            "d2": {"0": 1, "1": 0},
#            "d3": {"0": 0, "1": 1}
#        }
#    }

import time

# {"home_id": "homeid1", "device_visibility": {"192.168.1.118": {"38": "1"}, "192.168.1.102": {"38": "1"}, "192.168.1.104": {"38": "1"}, "192.168.1.106": {"38": "1"}, "192.168.1.146": {"38": "1"}, "192.168.1.1": {"38": "1"}}, "timestamp_hour": "2016-02-07T17:38:00"}

# loop every minute.
for count in range(1, 100000):
    time.sleep(60)
    nm.scan(hosts=network_addr_to_scan, arguments='-sP')
    print nm.all_hosts()
    visible_hosts = nm.all_hosts()
    curr_time = datetime.datetime.now()
    # round to the minute.
    hour = curr_time.hour
    minute = curr_time.minute
    curr_time = curr_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
    minute_value_map = {}
    home_doc_map = {}
    device_visibility_doc_map = {}
    # device_visibility_doc_map:-
    # { "d1": {"10": 1},
    #  "d2": {"10":1 }
    #  }
    for device in visible_hosts:
        minute_value_map[minute] = "1"
        # convert . to _ in the ip address
        # 
        formatted_device = device.replace(".", "_")
        #device_visibility_doc_map[device] = minute_value_map
        device_visibility_doc_map[formatted_device] = minute_value_map

        home_doc_map["home_id"] = home_id
        home_doc_map["timestamp_hour"] = curr_time.isoformat()
        home_doc_map["device_visibility"] = device_visibility_doc_map
        home_doc_json = json.dumps(home_doc_map)
        print(home_doc_json)
        if len(device_visibility_doc_map) > 0:
            # test = 1
            # we have some device visible, so post it to the server.
            resp = requests.post(url, data=home_doc_json)
            print(resp)
            if resp.status_code != 201 and resp.status_code != 200:
                raise ApiError('POST /tasks/ {}'.format(resp.status_code))
                # print('Created task. ID: {}'.format(resp.json()["id"]))
