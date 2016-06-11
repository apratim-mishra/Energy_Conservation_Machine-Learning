from __future__ import print_function

import os
import sys
import datetime

from pymongo import MongoClient
import json

# to run
# /home/bigdata/spark-1.5.2-bin-hadoop2.6/bin/pyspark --jars /home/bigdata/smart_home_app/spark-mongo-libs/mongo-hadoop-core-1.4.2.jar,/home/bigdata/smart_home_app/spark-mongo-libs/mongo-java-driver-2.13.2.jar cluster-home-devices.py

# need for pycharm
def configure_spark(spark_home=None, pyspark_python=None):
    spark_home = spark_home or "/path/to/default/spark/home"
    os.environ['SPARK_HOME'] = spark_home

    # Add the PySpark directories to the Python path:
    sys.path.insert(1, os.path.join(spark_home, 'python'))
    sys.path.insert(1, os.path.join(spark_home, 'python', 'pyspark'))
    sys.path.insert(1, os.path.join(spark_home, 'python', 'build'))

    # If PySpark isn't specified, use currently running Python binary:
    pyspark_python = pyspark_python or sys.executable
    os.environ['PYSPARK_PYTHON'] = pyspark_python


# import numpy as np
# configure_spark('/usr/local/spark-1.4.1-bin-hadoop2.6')
configure_spark('/home/bigdata/Downloads/spark-1.5.2-bin-hadoop2.6')
from pyspark import SparkContext, SparkConf
from pyspark.mllib.clustering import KMeans

"""
Returns mango document
[{u'home_id': u'home1id', u'device_visibility': {u'd2': {u'1': 0, u'0': 1, u'2': 1.0}, u'd3': {u'1': 1, u'0': 0}, u'd1': {u'1': 1, u'0': 1}}, u'_id': {u'timeSecond': 1442716814, u'timestamp': 1442716814, u'__class__': u'org.bson.types.ObjectId', u'machine': -1977956904, u'time': 1442716814000, u'date': datetime.datetime(2015, 9, 19, 19, 40, 14), u'new': False, u'inc': -1241015526}, u'timestamp_hour': u'2015-10-10T23:00:00.000Z'}]
"""


def get_device_stats_mongo_doc(s):
    return s[1]


# add weekday_hour with say 'weekday0-23hour'
def get_weekday_hourly_doc(s):
    try:
        date_obj = datetime.datetime.strptime(s['timestamp_hour'],
                                              "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        date_obj = datetime.datetime.strptime(s['timestamp_hour'],
                                              "%Y-%m-%dT%H:%M:%S")

    # s['timestamp_hour'] = "weekday" + str(date_obj.weekday()) + "-" + str(date_obj.hour) + "hour"
    s['weekday_hour'] = "weekday" + str(date_obj.weekday()) + "-" + str(date_obj.hour) + "hour"

    # print("weekday" + str(date_obj.weekday()) + "-" + str(date_obj.hour) + "hour")
    return s


def set_device_visibility_minute_array(s):
    device_visibility = s["device_visibility"]
    device_visibility_minute_array = []
    # import pdb; pdb.set_trace()
    # import rpdb; rpdb.set_trace()
    s["device_visibility_by_minute"] = {}
    #   import rpdb; rpdb.set_trace()
    for device in device_visibility:
        # print ("device:" + device)
        visibility_map = device_visibility[device]
        device_visibility_minute_array = []
        for minute in range(0, 59):
            if str(minute) in visibility_map:  # [str(minute)]:
                # print ("minute"+ str(minute))
                # print ("visibility:" + str(visibility_map[str(minute)]))
                to_append = visibility_map[str(minute)]
                device_visibility_minute_array.append(to_append)
            else:
                device_visibility_minute_array.append(0)

        s["device_visibility_by_minute"][device] = device_visibility_minute_array

    return s


def set_device_clusters(s, kmeans_model):
    # import rpdb; rpdb.set_trace()
    s['device_clusters'] = {}
    for (device_num, minute_values) in s['device_visibility_by_minute'].iteritems():
        s['device_clusters'][str(device_num)] = kmeans_model.predict(minute_values)

    return s

def save_in_mongodb(rdd):
    with MongoClient('localhost',27017) as db:
        # db = MongoClient('localhost',27017)
        dbconn = db.home_automation # should be database name
        deviceStatsCollection = dbconn['device_clusters'] # collection in DB
        # import rpdb; rpdb.set_trace()
        for i in range(0,rdd.count()):
            json_str = rdd.collect()[i]
            #json_obj = json.loads(json_str)
            #import rpdb; rpdb.set_trace()
            weekday_hour = rdd.collect()[i]["weekday_hour"]
            deviceStatsCollection.remove({"weekday_hour" : weekday_hour })
            deviceStatsCollection.insert(json_str)

    # db.close()

if __name__ == "__main__":
    # if len(sys.argv) != 3:
    #     print("Usage: kmeans <file> <k>", file=sys.stderr)
    #     exit(-1)
    # if len(sys.argv) != 2:
    #    print("Usage: kmeans <file>", file=sys.stderr)
    #    exit(-1)
    conf = SparkConf()

    sc = SparkContext(appName="cluster-home-devices")

    database_url = 'mongodb://127.0.0.1:27017/home_automation.device_stats'
    rdd = sc.newAPIHadoopRDD(
        inputFormatClass='com.mongodb.hadoop.MongoInputFormat',
        keyClass='org.apache.hadoop.io.Text',
        valueClass='org.apache.hadoop.io.MapWritable',
        conf={'mongo.input.uri': database_url, 'mongo.input.split.create_input_splits': 'false'})
        #conf={'mongo.input.uri': database_url})
    rdd.cache()
    # print("Hadoop RDD" + str(rdd.take(1)))
    rdd1 = rdd.map(get_device_stats_mongo_doc)
    rdd1.cache()  # needed as mongodb connector has bugs.
    # print("mongo_doc" + str(rdd1.take(1)))
    rdd2 = rdd1.map(get_weekday_hourly_doc)
    # print("weekday_hourly_doc" + str(rdd2.take(1)))
    rdd3 = rdd2.map(set_device_visibility_minute_array)
    # print("weekday_hourly_doc_device_minute" + str(rdd3.take(10)))

    rdd_home_weekly = rdd3;

    for weekday in range(0, 7):  # [0 to 6]
        for hour in range(0, 24):
            current_weekday_hour_string = "weekday" + str(weekday) + "-" + str(hour) + "hour"  # eg., 'weekday2-20hour'

            rdd_to_cluster = rdd_home_weekly.filter(lambda s: s['weekday_hour'] == current_weekday_hour_string)
            rdd_to_cluster_model = rdd_to_cluster.map(lambda s: s['device_visibility_by_minute'])
            rdd_to_cluster_model.cache() # need to do for MangoDB Connector bug (exception on multi operations)
            result_count = rdd_to_cluster_model.count()
            # print("data count=" + str(result_count) + " " + current_weekday_hour_string)
            # import rpdb; rpdb.set_trace()
            if result_count == 0:
                continue

            optimal_cost = 10000000
            optimal_clusters = 0

            # find optimal clusters for this hour interval (weekday-hour)
            for num_clusters in range(2, 20):

                k = num_clusters
                data = rdd_to_cluster_model.flatMap(lambda s: [v for (k, v) in s.iteritems()])
                data_count = data.count()
                # print("data count=" + str(data_count) + " " + current_weekday_hour_string)
                if data_count == 0:
                    continue
                # import rpdb; rpdb.set_trace()
                # print("data to train:" + data)
                model = KMeans.train(data, k)
                cost = model.computeCost(data)

                # predict_data = data.take(1)[0]
                # print("predict cluster number:" + str(model.predict(predict_data)))
                # print("num_clusters:" + str(num_clusters) + " Total Cost: " + str(cost))
                # print("Final centers: " + str(model.clusterCenters))
                # print("predict cluster: " + str(model.predict(data.collect()[0])))  # check cluster of first element
                if cost < 10 and optimal_cost > 100:
                    optimal_cost = cost
                    optimal_clusters = num_clusters
                    optimal_model = model
                if cost == 0:
                    optimal_cost = cost
                    optimal_clusters = num_clusters
                    optimal_model = model
                    break

            # import rpdb; rpdb.set_trace()
            print(current_weekday_hour_string + " optimal_clusters:" + str(optimal_clusters) +
                  " optimal_cost:" + str(optimal_cost))


            # You can pass additional parameters to flatMap/map function:
            rdd_with_device_clusters = rdd_to_cluster.map(lambda s: set_device_clusters(s, optimal_model))
            #rdd_with_device_clusters.cache()
            print(rdd_with_device_clusters.count())
            save_in_mongodb(rdd_with_device_clusters)
            # import rpdb; rpdb.set_trace()
            # Bugs 
            # Save this RDD as a Hadoop "file".
            # The path argument is unused; all documents will go to "mongo.output.uri".
            # rdd_with_device_clusters_values = rdd_with_device_clusters.values()
            # rdd_with_device_clusters_values.saveAsNewAPIHadoopFile(
            # # rdd_with_device_clusters.saveAsNewAPIHadoopFile(
            # #rdd.saveAsNewAPIHadoopFile(
            #      path='file:///this-is-unused',
            #      outputFormatClass='com.mongodb.hadoop.MongoOutputFormat',
            #      keyClass='org.apache.hadoop.io.Text',
            #      #keyClass='org.apache.hadoop.io.IntWritable',
            #      valueClass='org.apache.hadoop.io.MapWritable',
            #      #conf={'mongo.input.uri': database_url, 'mongo.input.split.create_input_splits': 'false'}
            #      conf={
            #          'mongo.output.uri': 'mongodb://127.0.0.1:27017/home_automation.device_clusters',
            #          #'mongo.input.split.create_input_splits': 'false'
            #      }
            #  )



    sc.stop()
