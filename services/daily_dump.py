import sys
from pymongo import MongoClient
import datetime

db = MongoClient('localhost', 27017)
dbconn = db.home_automation  # should be database name

#start_date="2016-12-17" 
start_date=sys.argv[1]
total_days=10
if len(sys.argv) == 3: 
    total_days=int(sys.argv[2])
#print "total_days:" + str(total_days)
home_id="teja"
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
                    
                # GOOD debug
                # print device + " " + hour + " minute_visibility:" + str(minute_visibility)  +  " minute_from_hour:" + str(minute_from_hour) + "  min_from_day_beg:" + str(minute_from_begining_of_day) + " day_number:" + str(day_number) + " min_from_start:" +str(minute_from_beginning_of_start_date) +  " =" + document['device_visibility'][device][minute_visibility]
                # TO verify: WeMo%20Insight 2016-12-02T23:00:00 minute_visibility:55 minute_from_hour:55  min_from_day_beg:1435 day_number:2 min_from_start:4315 =1
                # print (datetime.datetime.strptime("2016-12-02T23:55:00", "%Y-%m-%dT%H:%M:%S")-datetime.datetime.strptime("2016-11-30", "%Y-%m-%d")).total_seconds()/60
                # 4315.0

out = '{:31}'.format("all#day:hr")


for min  in range(0,max_minute_from_beginning_of_start_date):
    curr_day = min/1440
    curr_hour = (min%1440)/60
    if min%60 == 0:
        out = out + '{:2}'.format(curr_day) + ":" + '{:2}'.format(curr_hour)
    else:
        out = out + '{:5}'.format(min%60)

print out

for device in device_visibility_for_day:
    deviceName = device
    if device in names:
        deviceName =  names[device] + device
    out = deviceName

    # format  name in 31 chars
    out = '{:31}'.format(deviceName)

    for min_of_day in range(0,max_minute_from_beginning_of_start_date):
        out = out + ",   " + str(device_visibility_for_day[device].get(min_of_day, 0))
    print out



