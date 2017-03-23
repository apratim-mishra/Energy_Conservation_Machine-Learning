"""

client_home.py will send all the data to views.py which is running on AWS. 
Then views.py will put the data into MongoDB. 
Then daily_dump.py will read from mongoDB and it will write into 
daily_dump.txt which will be read by algorithms.py

By Tejasvi Kothapalli

"""
import sys
from pymongo import MongoClient
import datetime

db = MongoClient('localhost', 27017)
dbconn = db.home_automation  # should be database name

#start_date="2016-12-17" 
start_date=sys.argv[1]
total_days=10
#home_id="teja"
home_id="kart"

if len(sys.argv) == 3: 
    total_days=int(sys.argv[2])
if len(sys.argv) == 4: 
    total_days=int(sys.argv[2])
    home_id=sys.argv[3]

device_visibility_for_day={}
max_minute_from_beginning_of_start_date=0

names = dbconn.device_names.find_one({"home_id" : home_id})

for day_number in range(0,total_days):
 start_hour = 0
 end_hour=24
 for count in range(start_hour,end_hour): # hour
    curr_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d") + datetime.timedelta(days=day_number)
    curr_date = curr_date_obj.strftime("%Y-%m-%d")
    hour = curr_date + "T" + "%02d" % count  + ":00:00"
    cursor = dbconn.device_stats.find({"timestamp_hour": hour, "home_id" : home_id }, {"device_visibility":1,"_id":0 } )
    for document in cursor:
        for device in document['device_visibility']:
            for minute_visibility in document['device_visibility'][device]:
                minute_from_hour = int(minute_visibility)
                minute_from_begining_of_day = count * 60 +  minute_from_hour
                minute_from_beginning_of_start_date = count * 60 +  minute_from_hour + day_number*1440
                if device in device_visibility_for_day:
                    pass
                else:
                    device_visibility_for_day[device] = {}
                #device_visibility_for_day[device][minute_from_begining_of_day] = document['device_visibility'][device][minute_visibility]
                device_visibility_for_day[device][minute_from_beginning_of_start_date] = document['device_visibility'][device][minute_visibility]
                max_minute_from_beginning_of_start_date = max(minute_from_beginning_of_start_date,max_minute_from_beginning_of_start_date)
                    
                # GOOD for debug
                # print device + " " + hour + " minute_visibility:" + str(minute_visibility)  +  " minute_from_hour:" + str(minute_from_hour) + "  min_from_day_beg:" + str(minute_from_begining_of_day) + " day_number:" + str(day_number) + " min_from_start:" +str(minute_from_beginning_of_start_date) +  " =" + document['device_visibility'][device][minute_visibility]
                # TO verify: WeMo%20Insight 2016-12-02T23:00:00 minute_visibility:55 minute_from_hour:55  min_from_day_beg:1435 day_number:2 min_from_start:4315 =1
                # print (datetime.datetime.strptime("2016-12-02T23:55:00", "%Y-%m-%dT%H:%M:%S")-datetime.datetime.strptime("2016-11-30", "%Y-%m-%d")).total_seconds()/60
                # 4315.0

out = '{:31}'.format("1all#day:hr:min,")


for min  in range(0,max_minute_from_beginning_of_start_date):
    curr_day = min/1440
    curr_hour = (min%1440)/60
    out = out + '{:02d}'.format(curr_day) + ":" + '{:02d}'.format(curr_hour) + ":" + '{:02d}'.format(min%60) + ","

print out

for device in device_visibility_for_day:
    deviceName = device

    if names is not None:
        if device in names:
            deviceName =  names[device] + device
    out = deviceName

    # format  name in 31 chars
    out = '{:31}'.format(deviceName)

    for min_of_day in range(0,max_minute_from_beginning_of_start_date):
        out = out + ",       " + str(device_visibility_for_day[device].get(min_of_day, 0))
    print out


# do this for web UI Access otherwise . web will not have data.
# sys.exit(0)

"""

Plot daily device visibility graph

"""

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Get current size
fig_size = plt.rcParams["figure.figsize"]
# Set figure width to 12 and height to 9
fig_size[0] = 12
fig_size[1] = 9
plt.rcParams["figure.figsize"] = fig_size
plt.rcParams['axes.labelsize'] = 'x-large'
plt.rc('font', weight='bold')
plt.rc('axes', linewidth=2)  
plt.rc('xtick', labelsize=20)
plt.rc('ytick', labelsize=18)
plt.rcParams['ytick.color'] = 'black'
plt.rcParams['xtick.color'] = 'black'

plt.rc('lines', lw=2, color='g')
plt.rc('savefig', dpi=300)  # higher res outputs

plt.axis([0, max_minute_from_beginning_of_start_date, 0, len(device_visibility_for_day)+1]) # xmin, xmax, ymin, ymax

device_number=1
y_number=[]
y_ticks=[]
for device in device_visibility_for_day:
    deviceName = device

    if names is not None:
        if device in names:
            #deviceName =  names[device] + device
            deviceName =  names[device]

    y_number.append(device_number)
    y_ticks.append(deviceName)
    for min_of_day in range(0,max_minute_from_beginning_of_start_date):
        if device_visibility_for_day[device].get(min_of_day, 0) != 0:

            plt.scatter(min_of_day, device_number, marker='.', color='blue', alpha=0.7, s = 20)

    device_number = device_number+1

font = {'family': 'serif',
        'color':  'darkred',
        'weight': 'normal',
        'size': 36,
        }

plt.xlabel("Minute of the day", fontdict=font)
plt.ylabel("Wi-Fi Devices ", fontdict=font)
plt.yticks(y_number, y_ticks)

# very good to see all properties.
# for param, value in plt.rcParams.items():
#     print param, value


plt.subplots_adjust(left=0.25)

plt.savefig('/home/ubuntu/Energy_Conservation_Machine-Learning/smart_home_app/static/daily')
plt.close()


