from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from pymongo import MongoClient
import json
import datetime
import pymongo
import subprocess
from django.http import JsonResponse

#@csrf_exempt
@api_view(['GET', 'POST'])
def smart_home_api(request):
    # connect to our local mongodb
    db = MongoClient('localhost', 27017)
    # get a connection to our database
    dbconn = db.home_automation  # should be database name
    device_stats_collection = dbconn['device_stats']  # collection in DB


    if request.method == 'GET' and request.GET['op'] == 'compute_clusters':
        day=request.GET['day'] # eg., "2016-08-20"
	home_id = "teja"
        cmd = "/home/ubuntu/spark-1.5.2-bin-hadoop2.6/bin/pyspark --executor-memory 100M --jars /home/ubuntu/Energy_Conservation_Machine-Learning/spark-mongo-libs/mongo-hadoop-core-1.4.2.jar,/home/ubuntu/Energy_Conservation_Machine-Learning/spark-mongo-libs/mongo-java-driver-2.13.2.jar  /home/ubuntu//Energy_Conservation_Machine-Learning/services/cluster-home-devices-by-day.py " + day

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).communicate()
        #p.wait(timeout=3000)
        return Response(p)        

    if request.method == 'GET' and request.GET['op'] == 'hourly_data':
        # For every one should the visitbility data
        # Eg., db.device_clusters.find({"timestamp_hour":"2016-07-01T22:00:00", "home_id":"teja"},{"device_visibility_by_minute":1,"_id":0 } ).pretty()
        # db.device_clusters.find({"timestamp_hour":"2016-07-01T02:00:00", "home_id":"teja"},{"device_visibility_by_minute":1,"_id":0 } ).pretty()
        day=request.GET['day'] # eg., "2016-08-20"
	home_id = "teja"
        db = MongoClient('localhost', 27017)
        dbconn = db.home_automation  # should be database name
        device_stats_collection = dbconn['device_stats']  # collection in DB
        #hour = day + "T01:00:00"
        hour = "2016-07-01T02:00:00"
        hour = day + "T" + "02" + ":00:00"
        out = ""
        for count in range(0,24): # hour
            hour = day + "T" + "%02d" % count  + ":00:00"
            #print day + "T" + "%02d" % count  + ":00:00"

            print hour
            
            device_cluster_map = {}
            # find the device and its cluster for the hour
            cursor = dbconn.device_clusters.find({"timestamp_hour": hour, "home_id" : home_id }, {"device_clusters":1,"_id":0 } )
            for document in cursor:
                for device in document['device_clusters']:  
                    #print device + " " + str(document['device_clusters'][device])
                    device_cluster_map[device] = document['device_clusters'][device]

            # now find the device visitibility for the hour (for every minute)
            cursor = dbconn.device_clusters.find({"timestamp_hour": hour, "home_id" : home_id }, {"device_visibility_by_minute":1,"_id":0 } )


            out =  out + "<table border=0>"

            out = out + "<tr>"
            out = out + "<td>" +  hour + "</td>"
            out = out + "<td>" +  "cluster" + "</td>"
            for minute in range(1,60):
                out = out + "<td>" +  str(minute) + "</td>"
            out = out + "</tr>"

            for document in cursor:
                for device in document['device_visibility_by_minute']:
                    out = out + "<tr>"
                    out = out + "<td>" +  device + "</td>" 
                    out = out + "<td>cluster" +  str(device_cluster_map[device]) + "</td>" 
                    for minute_visibility in document['device_visibility_by_minute'][device]:
                        out = out + "<td>" + str(minute_visibility) + "</td>"
                out = out + "</tr>"
            out =  out + "</table>"
            #print out
        return Response(out)

    if request.method == 'GET' and request.GET['op'] == 'graph':

# returns data in this format:-
# {"cols":[{"type":"string","id":"IP_Address"},{"type":"date","id":"Start"},{"type":"date","id":"End"}],"rows":[
# {"c":[{"v":"192_168_1_107"},{"v":"Date(2016,06,13,00,12,0)"},{"v":"Date(2016,06,13,00,12,0)"}]},
# {"c":[{"v":"192_168_1_107"},{"v":"Date(2016,06,13,00,28,0)"},{"v":"Date(2016,06,13,00,28,0)"}]},
# {"c":[{"v":"192_168_1_107"},{"v":"Date(2016,06,13,00,39,0)"},{"v":"Date(2016,06,13,00,39,0)"}]},
# ]}

        # from 2016-06-25 - 2016-07-02
        # "2016-06-28", "2016-06-27", "2016-06-26", 06-29, 06-30, 07-01, 07-02
         
        #day = "2016-07-01"
        #day = "2016-06-28"
        #day = "2016-08-20"
        day=request.GET['day'] # eg., "2016-08-20"
	home_id = "teja"
        db = MongoClient('localhost', 27017)
        dbconn = db.home_automation  # should be database name
        device_stats_collection = dbconn['device_stats']  # collection in DB
        cursor = dbconn.device_stats.find({"timestamp_hour": {'$regex': day}, "home_id" : home_id }).sort([("timestamp_hour", pymongo.ASCENDING)])
        names = dbconn.device_names.find_one({"home_id" : home_id})
#cursor = dbconn.device_stats.find({"timestamp_hour" : "2016-06-10T22:00:00"})
        output = ""
        output += '{"cols":[{"type":"string","id":"IP_Address"},{"type":"string","id":"Cluster_Name"},{"type":"date","id":"Start"},{"type":"date","id":"End"}], \n "rows":['

        for document in cursor:
                devicesList = document['device_visibility']

                timestamp_hour = document['timestamp_hour'] 
                try:
                    date_obj = datetime.datetime.strptime(timestamp_hour,
                                                  "%Y-%m-%dT%H:%M:%S.%fZ")
                except ValueError:
                    date_obj = datetime.datetime.strptime(timestamp_hour,
                                                          "%Y-%m-%dT%H:%M:%S")
                # weekday0-19hour
                weekday_hour = "weekday" + str(date_obj.weekday()) + "-" + str(date_obj.hour) + "hour"
                # find device cluster if already computed
                #print "weekday_hour:"+weekday_hour

                # Eg., db.device_clusters.find({"weekday_hour" : "weekday2-0hour"})
                device_cluster_obj = dbconn.device_clusters.find_one({"weekday_hour" : weekday_hour})
                #import rpdb; rpdb.set_trace()
                
                for device in devicesList:
                        timesON = sorted(devicesList[device])
                        for time in timesON:
                                year = document['timestamp_hour'][:4]
                                month = document['timestamp_hour'][5:-12]
                                day = document['timestamp_hour'][8:-9]
                                hour = document['timestamp_hour'][11:-6]
				deviceName = ""
                                if device in names:
                                    deviceName = names[device]
                                ipRow = '{"v":"' +  deviceName + " ("+ device + ")" + '"}'
                                cluster = ""
                                if device_cluster_obj is not None and 'device_clusters' in device_cluster_obj and device in device_cluster_obj['device_clusters']:
                                    cluster = device_cluster_obj['device_clusters'][device]
                                
                                cluster_name = '{"v":"' +  str(cluster)  + '"}' # TODO fix
                                startDate = '{"v":"Date('+ year + ',' + month + ',' + day + ',' + hour + ',' + time + ',0)"}'
                                output += '{"c":['+ ipRow + ',' + cluster_name + ',' + startDate + ',' + startDate + ']}, \n'
        output +=  "]}" 
        # remove last comma (,). Otherwise json parsing fails.
        last_occurance = output.rfind(",")
        output = output[:last_occurance] + "" + output[last_occurance+1:]
        
        #print output
        try:
            json_obj = json.loads(output)
        except:
            print output
        return JsonResponse(json_obj)

    if request.method == 'POST':
        json_str = (request.body.decode('utf-8'))
        # print "***" + json_str + "***"
        json_obj = json.loads(json_str)

        # import pdb; pdb.set_trace()        
        # deviceStatsCollection.insert(json_obj)
        # {"home_id" : "home1id",
        #  "timestamp_hour": "2015-10-10T23:00:00.000Z",
        #  "device_visibility": {
        #      "d1": {"0":1, "1":1},
        #      "d2": {"0":1, "1":0},
        #      "d3": {"0":0, "1":1}
        #  }
        # }

        # import pdb; pdb.set_trace()
        # convert to upsert
        home_id = json_obj['home_id']
        timestamp_hour = json_obj['timestamp_hour']
        print(timestamp_hour)
        # round to hour (strip off minute, second, micro second)
        #
        try:
            date_obj = datetime.datetime.strptime(timestamp_hour,
                                                  "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            date_obj = datetime.datetime.strptime(timestamp_hour,
                                                  "%Y-%m-%dT%H:%M:%S")
        timestamp_hour = date_obj.replace(year=date_obj.year,
                                          month=date_obj.month, day=date_obj.day,
                                          hour=date_obj.hour, minute=0, second=0, microsecond=0).isoformat()
        weekday_hour = "weekday" + str(date_obj.weekday()) + "-" + str(date_obj.hour) + "hour"

        print(timestamp_hour + " weekday_hour:" + weekday_hour)


        device_visibility = json_obj['device_visibility']
        device_visibility_upsert_set = {}
        for key in json_obj['device_visibility'].keys():
            # import pdb; pdb.set_trace()
            for key1 in json_obj['device_visibility'][key].keys():
                device_minute_key = "device_visibility." + key + "." + key1
                device_minute_value = device_visibility[key][key1]
                device_visibility_upsert_set[device_minute_key] = device_minute_value

        print  device_visibility_upsert_set
        device_stats_collection.update({"home_id": home_id, "timestamp_hour": timestamp_hour},
                                     {"$set": device_visibility_upsert_set},
                                     upsert=True)

        # import pdb; pdb.set_trace() 
        # import rpdb; rpdb.set_trace()
        device_clusters_collection = dbconn['device_clusters']  # collection in DB
        device_custers_obj = device_clusters_collection.find_one({"weekday_hour" : weekday_hour})
        if device_custers_obj is not None:
            response_string = {"ok": "true"}
            # check if the device is on the old training data at the same minute
            for device in json_obj['device_visibility'].keys():
                for minute in json_obj['device_visibility'][device].keys():

                    if device in  device_custers_obj['device_visibility_by_minute']:
                        # import rpdb; rpdb.set_trace()
                        int_minute = int(minute)
                        device_minute_value = device_visibility[device][minute]
                        past_device_minute_value = device_custers_obj['device_visibility_by_minute'][device][int_minute]
                        if int(device_minute_value) == 1 and past_device_minute_value == 0:
                            response_string[str(device)] = "switch off"

            return Response(response_string)

        return Response({"ok": "true"})

        # see http://api.mongodb.org/python/current/tutorial.html
        # deviceStatsCollection.insert({"home_id" : 1234, "address": 1235})
        # post_id = deviceStatsCollection.insert(json_obj).inserted_id
        # print "***" + post_id + "***"
