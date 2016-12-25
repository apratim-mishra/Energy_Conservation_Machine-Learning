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
#
#sudo bash
#while [ 1 ]
#do  
#    python client_home.py
#    sleep 2
#done

# python client_home1.py 
# ['192.168.1.1', '192.168.1.104', '192.168.1.106', '192.168.1.107', '192.168.1.109', '192.168.1.118', '192.168.1.119', '192.168.1.145', '192.168.1.146']


nm = nmap.PortScanner()
home_id = "teja"
network_addr_to_scan = "192.168.1.1/24"
#url = "http://localhost:8000/smart_home_app/?"
url = "http://54.201.150.12:8043/smart_home_app/?"

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
#for count in range(1, 100000):
while True:
    #time.sleep(60)
    time.sleep(30)
    nm.scan(hosts=network_addr_to_scan, arguments='-sP')
    print nm.all_hosts()

    # for ip address only: run as non-root
    visible_hosts = nm.all_hosts()

    # For mac addresses: run as root
    # http://stackoverflow.com/questions/26198714/how-to-retrieve-mac-addresses-from-nearby-hosts-in-python
    visible_hosts = []
    for h in nm.all_hosts():
        if 'mac' in nm[h]['addresses']:
            #print(nm[h]['addresses']['mac'])
            visible_hosts.append(nm[h]['addresses']['mac'])
        else: # no mac address known
            #print "no mac" +  str(nm[h]['addresses'])
            #print nm[h]['addresses']['ipv4']
            visible_hosts.append(nm[h]['addresses']['ipv4'])



    curr_time = datetime.datetime.now()
    # round to the minute.
    hour = curr_time.hour
    minute = curr_time.minute
    curr_time = curr_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
    minute_value_map = {}
    home_doc_map = {}
    device_visibility_doc_map = {}
    # device_visibility_doc_map:-
    # "device_visibility": {"192_168_1_118": {"52": "1"}, "192_168_1_119": {"52": "1"}, "192_168_1_137": {"52": "1"}, "192_168_1_126": {"52": "1"}, "192_168_1_1": {"52": "1"}, "192_168_1_145": {"52": "1"}}
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

    # Add wemo power states also
    import urllib2
    import json
    wemo_url_list  = ["http://localhost:5000/api/device/WeMo%20Insight"]

    for wemo in wemo_url_list:
        try :
            minute_value_map[minute] = "1"
            response = urllib2.urlopen(wemo).read()
            #print "wemo response" + wemo + ":" + response
            json_obj = json.loads(response)
            # is the wemo powered on ?
            #print "wemo current state" + str(json_obj["state"])
            if json_obj["state"] == 1:
                # get the last port of the wemo after "/" eg., WeMo%20Insight
                formatted_device = wemo.rsplit('/', 1)[-1]
                device_visibility_doc_map[formatted_device] = minute_value_map 
                home_doc_map["device_visibility"]  =  device_visibility_doc_map 

        except:
            # ignore not able to access the wemo device
            print "start wemo server nohup wemo server &"
            print "check: curl http://localhost:5000/api/environment "
            print "ping wemo ip 101"
            #pass


    # send the info to a server
    home_doc_json = json.dumps(home_doc_map)
    print(home_doc_json)
    if len(device_visibility_doc_map) > 0:
        # test = 1
        # we have some device visible, so post it to the server.
        resp = requests.post(url, data=home_doc_json, headers={'Connection':'close'})
        #print(resp)
        if resp.status_code != 201 and resp.status_code != 200:
            print (resp.status_code)
            pass
            #raise ApiError('POST /tasks/ {}'.format(resp.status_code))
            # print('Created task. ID: {}'.format(resp.json()["id"]))
