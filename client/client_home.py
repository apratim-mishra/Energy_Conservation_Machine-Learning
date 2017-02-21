import os
import requests
import datetime
import json
import random
import sys
#import nmap
import subprocess
import time




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


# $ ifconfig wlan0
# wlan0     Link encap:Ethernet  HWaddr 20:16:d8:15:94:66  
#           inet addr:192.168.1.137  Bcast:192.168.1.255  Mask:255.255.255.0
#           inet6 addr: fe80::2216:d8ff:fe15:9466/64 Scope:Link
def getNetworkAddress(interface):
    cmd="ifconfig   " + interface
    network_address = ""
    ifconfig_out= subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
    for line in ifconfig_out.splitlines():
        if 'inet addr:' in line:
            network_address =line.split(":")[1].split()[0]
    return network_address + "/24" #/24 bc since each set of num before . is 8 bytes and you want the first 3 8 bytes as network address


def getWemoStatusMap():
    cmd = "wemo status"
    wemo_status_output=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
    # $ wemo status 
    # Switch: WeMo Insight 	0
    wemo_status_map = {}
    for line in wemo_status_output.splitlines():
        if 'Switch' in line:
            arr=line.split(":")[1].split("\t")
            wemo_name = arr[0]
            wemo_name = wemo_name.strip()
            wemo_name = wemo_name.replace(" ", "%20") 
            # WeMo Insight  ->  WeMo%20Insight 
            wemo_status=arr[1].strip()
            wemo_status_map[wemo_name]=wemo_status

    return wemo_status_map

def wemoChangePower(wemo_name, power_state):
    # wemo switch "WeMo%20Insight" off
    # wemo switch "WeMo%20Insight" on
    wemo_name = wemo_name.strip()
    wemo_name = wemo_name.replace("%20", " ")
    cmd = "wemo switch " + "\"" + wemo_name + "\" " + power_state
    wemo_status_output=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
    print cmd, wemo_status_output

if len(sys.argv) != 2:
#    print "Usage: " + sys.argv[0] + " home_id"
	print "You need two arguements (ie. " + sys.argv[0] + " teja)"    
	sys.exit()

home_id = sys.argv[1]
#home_id = "teja"

network_interface="wlan0"
print getNetworkAddress(network_interface)

# network_addr_to_scan = "192.168.1.1/24"
network_addr_to_scan = getNetworkAddress(network_interface)

#url = "http://localhost:8000/smart_home_app/?"
#url = "http://54.201.150.12:8043/smart_home_app/?"
url = "http://54.212.246.50:8043/smart_home_app/?" #?




# print "RUN ME AS ROOT !!!!!"



wemo_controller_device_similarity = { "WeMo%20Insight" : ["64:BC:0C:67:97:BC", "B8:E8:56:43:49:08"] 
}

wemo_controller_device_similarity_last_visible_time = { }

for wemo in wemo_controller_device_similarity:
    wemo_controller_device_similarity_last_visible_time[wemo] = datetime.datetime(2000, 1, 1)
    


use_nmap = False


last_power_off_time = datetime.datetime(2000, 1, 1)
prev_day_of_month=0
curr_day_of_month=0

# loop every minute.
#for count in range(1, 100000):
while True:
    #time.sleep(60)
    time.sleep(30)

    # random number to decide if today we can turn off the wemo
    curr_day_of_month=datetime.datetime.now().day # Eg., 18th 
    if curr_day_of_month != prev_day_of_month:
        prev_day_of_month = curr_day_of_month
        random_number = int(random.uniform(1, 100))
        print random_number, " random_number"
        if random_number%2 == 1:
            is_ok_to_tunr_off_today = 1
            print datetime.datetime.now(), " Today applying the machine learning algo to turrn off device."
        else:
            is_ok_to_tunr_off_today = 0
            print datetime.datetime.now(), " Today not applying the machine learning algo to turrn off device."
    
    if use_nmap:
        import nmap
        nm = nmap.PortScanner()
        # To debug in root: nmap  --send-ip  -sP   "192.168.1.1-255"
        # verify with :for i in $(seq 101 145); do ping -c1 -t 1 192.168.1.$i; done
        #nm.scan(hosts=network_addr_to_scan, arguments='-sP')
        nm.scan(hosts=network_addr_to_scan, arguments=' --send-ip -sP')
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

    else: # uses fping
        # apt-get install fping
        import subprocess
        cmd =  "fping -q -a -A -c1 -t500 -g " + network_addr_to_scan
        fping_out= subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE).stderr.read()

        ips_alive=[]
        for line in fping_out.splitlines():
            # fping -q -a -A -c1 -t500 -g "192.168.1.0/24" 
            # 192.168.1.103 : xmt/rcv/%loss = 1/1/0%, min/avg/max = 4.30/4.30/4.30
            # 192.168.1.104 : xmt/rcv/%loss = 1/0/100%
            if 'min/avg/max' in line:
                #print line
                #print line.split()[0]
                ips_alive.append(line.split()[0])

        ip_mac_map = {}
        arp_out= subprocess.Popen("arp -n", shell=True, stdout=subprocess.PIPE).stdout.read()
        for line in arp_out.splitlines():
            # arp -n | grep -v incomplete
            # Address                  HWtype  HWaddress           Flags Mask            Iface
            # 192.168.1.112            ether   c0:56:27:b4:a5:79   C                     wlan0
            # 192.168.1.103            ether   ac:bc:32:b4:01:27   C                     wlan0
            curr_ip = line.split()[0]
            curr_mac = line.split()[2]
            ip_mac_map[curr_ip] = curr_mac
            #print curr_ip + " " + curr_mac

        macs_alive = []
        for ip in ips_alive:
            default_value = ip
            mac_alive = ip_mac_map.get(ip, default_value)
            mac_alive = mac_alive.upper()
            macs_alive.append(mac_alive)
        visible_hosts=macs_alive

        

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
    wemo_status_map = getWemoStatusMap()
    for wemo in wemo_status_map:
        print "new wemo current state:" + wemo + ":" + wemo_status_map[wemo]
        if wemo_status_map[wemo] == "1":
            minute_value_map[minute] = "1"
            device_visibility_doc_map[wemo] = minute_value_map 
            home_doc_map["device_visibility"]  =  device_visibility_doc_map 
            
    # # Add wemo power states also
    # import urllib2
    # import json
    # wemo_url_list  = ["http://localhost:5000/api/device/WeMo%20Insight"]
    # # wemo_url_list  = ["http://localhost:5000/api/device/WeMo%20Insight", "http://localhost:5000/api/device/WeMo%20Switch1"]

    # for wemo in wemo_url_list:
    #     try :
    #         minute_value_map[minute] = "1"
    #         response = urllib2.urlopen(wemo).read()
    #         #print "wemo response" + wemo + ":" + response
    #         json_obj = json.loads(response)
    #         # is the wemo powered on ?
    #         formatted_device = wemo.rsplit('/', 1)[-1]
    #         print "wemo current state:" + formatted_device + ":" + str(json_obj["state"])
    #         if json_obj["state"] == 1:
    #             # get the last port of the wemo after "/" eg., WeMo%20Insight
    #             formatted_device = wemo.rsplit('/', 1)[-1]
    #             device_visibility_doc_map[formatted_device] = minute_value_map 
    #             home_doc_map["device_visibility"]  =  device_visibility_doc_map 

    #     except:
    #         # ignore not able to access the wemo device
    #         print "start wemo server nohup wemo server &"
    #         print "check: curl http://localhost:5000/api/environment "
    #         print "ping wemo ip 101"
    #         #pass


    # send the info to a server
    home_doc_json = json.dumps(home_doc_map)
    print(home_doc_json)
    if len(device_visibility_doc_map) > 0:
        # test = 1
        # we have some device visible, so post it to the server.
        resp = requests.post(url, data=home_doc_json, headers={'Connection':'close'})
        if resp.status_code != 201 and resp.status_code != 200:
            print (resp.status_code), resp.content
            print "Getting errors: Existing"
            sys.exit()
            pass
            #raise ApiError('POST /tasks/ {}'.format(resp.status_code))
            # print('Created task. ID: {}'.format(resp.json()["id"]))

        # Check if we can turn off the wemo
        # tejpho and tejmac similar to wemo insight
        # fill the last time the devices are visible (similar devices corresponding to wemo)
        # "WeMo%20Insight" -> Feb 19, 2017 6:00 pm
        # "WeMo%20Insight1" -> Feb 19, 2017 6:01 pm
        for wemo in wemo_controller_device_similarity:
             similar_devices = wemo_controller_device_similarity[wemo]
             for similar_device in similar_devices:
                 if similar_device in device_visibility_doc_map:
                     wemo_controller_device_similarity_last_visible_time[wemo] = curr_time
        
        last_power_off_mins_diff = (curr_time-last_power_off_time).total_seconds()/60 
        # if the devices corresponding to wemo are not visible turn off the wemo
        for wemo in wemo_controller_device_similarity:
            wemo_dependant_devices_last_visible_time = wemo_controller_device_similarity_last_visible_time[wemo]
            mins_since_devices_invisible=(curr_time-wemo_dependant_devices_last_visible_time).total_seconds()/60
            if mins_since_devices_invisible > 15 and last_power_off_mins_diff > 60 and is_ok_to_tunr_off_today == 1:
                # 
                print curr_time, " ", wemo, " devices ", wemo_controller_device_similarity[wemo], " are not visible for more than 15 mins. turning off now"
                wemoChangePower(wemo, "off")
                last_power_off_time = datetime.datetime.now()
    
                
        # power off only on even days
        # day_of_month = curr_time.day # eg., 18th
        # last_power_off_mins_diff = (curr_time-last_power_off_time).total_seconds()/60 
        # if  day_of_month%2 ==0 and last_power_off_mins_diff > 60:
        #  for wemo in wemo_controller_device_similarity:
        #      similar_devices = wemo_controller_device_similarity[wemo]
        #      all_similar_device_off = 1
        #      for similar_device in similar_devices:
        #          if similar_device in device_visibility_doc_map:
        #              all_similar_device_off = 0
        #      if all_similar_device_off == 1: # turn off wemo as all dependant devices are invisible
        #          wemoChangePower(wemo, "off")
        #          last_power_off_time = datetime.datetime.now()
        #          # cool off for next 1 hour
                
