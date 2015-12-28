from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from pymongo import MongoClient
import json
import datetime


@csrf_exempt
@api_view(['GET', 'POST'])
def smart_home_api(request):
    # connect to our local mongodb
    db = MongoClient('localhost', 27017)
    # get a connection to our database
    dbconn = db.home_automation  # should be database name
    device_stats_collection = dbconn['device_stats']  # collection in DB

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
        print(timestamp_hour)

        device_visibility = json_obj['device_visibility']
        device_visibility_upsert_set = {}
        for key in json_obj['device_visibility'].keys():
            # import pdb; pdb.set_trace()
            for key1 in json_obj['device_visibility'][key].keys():
                device_minute_key = "device_visibility." + key + "." + key1
                device_minute_value = device_visibility[key][key1]
                device_visibility_upsert_set[device_minute_key] = device_minute_value

        # print  device_visibility_upsert_set
        device_stats_collection.update({"home_id": home_id, "timestamp_hour": timestamp_hour},
                                     {"$set": device_visibility_upsert_set},
                                     upsert=True)

        return Response({"ok": "true"})

        # see http://api.mongodb.org/python/current/tutorial.html
        # deviceStatsCollection.insert({"home_id" : 1234, "address": 1235})
        # post_id = deviceStatsCollection.insert(json_obj).inserted_id
        # print "***" + post_id + "***"
