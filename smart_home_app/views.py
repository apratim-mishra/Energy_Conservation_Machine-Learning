from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from pymongo import MongoClient
import json
import datetime
import pymongo
from django.http import JsonResponse

#@csrf_exempt
@api_view(['GET', 'POST'])
def smart_home_api(request):
    # connect to our local mongodb
    db = MongoClient('localhost', 27017)
    # get a connection to our database
    dbconn = db.home_automation  # should be database name
    device_stats_collection = dbconn['device_stats']  # collection in DB
    #print "HELLO"

    if request.method == 'GET':

# returns data in this format:-
# {"cols":[{"type":"string","id":"IP_Address"},{"type":"date","id":"Start"},{"type":"date","id":"End"}],"rows":[
# {"c":[{"v":"192_168_1_107"},{"v":"Date(2016,06,13,00,12,0)"},{"v":"Date(2016,06,13,00,12,0)"}]},
# {"c":[{"v":"192_168_1_107"},{"v":"Date(2016,06,13,00,28,0)"},{"v":"Date(2016,06,13,00,28,0)"}]},
# {"c":[{"v":"192_168_1_107"},{"v":"Date(2016,06,13,00,39,0)"},{"v":"Date(2016,06,13,00,39,0)"}]},
# ]}

        day = "2016-07-01"
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
        json_obj = json.loads(output)
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
