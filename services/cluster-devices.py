#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ##ubuntu@ip-172-31-33-227:~/home-automation$ ~/spark-1.4.1-bin-hadoop2.6/bin/spark-submit cluster-devices.py home2-data.txt 3 
# /usr/local/spark-1.4.1-bin-hadoop2.6/bin/spark-submit  cluster-devices.py home1-data.txt 
"""
A K-means clustering program using MLlib.

This example requires NumPy (http://www.numpy.org/).
"""
from __future__ import print_function

import sys

import numpy as np
from pyspark import SparkContext
from pyspark.mllib.clustering import KMeans


def parseVector(line):
    return np.array([float(x) for x in line.split(' ')])


if __name__ == "__main__":
    # if len(sys.argv) != 3:
    #     print("Usage: kmeans <file> <k>", file=sys.stderr)
    #     exit(-1)
    if len(sys.argv) != 2:
        print("Usage: kmeans <file>", file=sys.stderr)
        exit(-1)

    sc = SparkContext(appName="cluster-devices")
    optimal_cost = 10000000
    optimal_clusters = 0
    for num_clusters in range(2,20):
        lines = sc.textFile(sys.argv[1])
        data = lines.map(parseVector)
        k = num_clusters
        print (data)
        # import rpdb; rpdb.set_trace()
        # (Pdb) data.collect()
        # [array([ 1.,  0.,  1.,  0.]), array([ 0.,  0.,  0.,  0.]), array([ 1.,  0.,  1.,  0.]), array([ 0.,  0.,  0.,  0.])]
        model = KMeans.train(data, k)
        cost = model.computeCost(data)
        print("num_clusters:" + str(num_clusters) + " Total Cost: " + str(cost))
        # print("Final centers: " + str(model.clusterCenters))
        print("predict cluster: " + str(model.predict( data.collect()[0] )) ) # check cluster of first element
        if (cost < 10 and optimal_cost > 100):
            optimal_cost = cost
            optimal_clusters = num_clusters
        if (cost == 0):
            break

    
    print("optimal_clusters:" + str(optimal_clusters) + " optimal_cost:" + str(optimal_cost))
            
            
        
    sc.stop()
