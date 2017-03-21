# Ref: https://github.com/adobe-research/spark-cluster-deployment/blob/master/initial-deployment-puppet/modules/spark/files/spark/examples/src/main/python/mllib/kmeans.py
# cd /home/ubuntu/Energy_Conservation_Machine-Learning/services
# python daily_dump.py "2016-12-23"  > /tmp/1223.txt
# /home/ubuntu/spark-1.5.2-bin-hadoop2.6/bin/pyspark cluster-devices-daily.py /tmp/1130.txt 5
"""
A K-means clustering program using MLlib.
This example requires NumPy (http://www.numpy.org/).
"""

import sys

import numpy as np
from pyspark import SparkContext
from pyspark.mllib.clustering import KMeans


def parseVector(line):
    return np.array([x for x in line.split(',')])[1:]


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print >> sys.stderr, "Usage: kmeans <file> <k>"
        exit(-1)
    sc = SparkContext(appName="KMeans")
    lines = sc.textFile(sys.argv[1])
    data = lines.map(parseVector)
    k = int(sys.argv[2])
    model = KMeans.train(data, k)
    print "Final centers: " + str(model.clusterCenters)
    #import rpdb; rpdb.set_trace() 
    
    total_device_count = len(lines.collect())
    for cluster_num in range(0,k):
        print "cluster:" + str(cluster_num) + " "
        for device_num in range(0,total_device_count):
            if model.predict(data.collect()[device_num]) == cluster_num:
                print " " + lines.collect()[device_num].split(",")[0]
