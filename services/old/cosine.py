import numpy as np
import scipy
import os
from sklearn.metrics.pairwise import cosine_similarity


def readfile(filename):
    f = open(filename, 'r')
    lines = f.readlines()
    d = {}
    for l in lines:
        elems = l.split(',')
        d[elems[0].strip()] = map(float, np.array(elems[1:]))
    return d

def setInterval(d, interval):
    for k in d:
        res = []
        i = 0
        while i < len(d[k]):
            res.append(0)
            for j in range(i, min(i + interval, len(d[k]))):
                if d[k][j] == 1:
                    res[len(res) - 1] =  1
                    break
            i = i + interval
        d[k] = res

def getIntervals(d, interval, wemo):
    for w in wemo:
        for i in range(0, len(d) - 1):
            if d[w][i] != d[w][i + 1]:
                    start_interval = max(0, i - interval)
                    end_interval = min(len(d), i + interval)
                    print("intervals/" + str(w) + "_" + str(i)+ ".txt")
                    f = open( "intervals/" + str(w) + "_" + str(i)+ ".txt", 'w')
                    f.write(str(w) + " " + str(d[w][start_interval : end_interval]) + "\n")
                    for device in d:
                        if device != w:
                            f.write(str(device) + " " + str(d[device][start_interval : end_interval]) + "\n")
                    f.close()
                

    
                
def writeCosine(filename, dictionary, wemo):
    f = open(filename, "w")
    arr = []
    for w in wemo:
        for device in dictionary:
            if device != w:
                sim = cosine_similarity(d[w], d[device])[0][0]
                arr.append((sim, str(w) + " " + str(device) + " : " + str(sim) + "\n"))
    arr.sort(reverse=True, key=lambda x : x[0])    
    for e in arr:
        f.write(e[1])
    

d = readfile("/tmp/dec2829.txt")
setInterval(d, 1)
getIntervals(d, 15,["tejlightWeMo%20Insight", "sunlightWeMo%20Switch1"])
writeCosine("cosine_similarity.txt", d, ["tejlightWeMo%20Insight", "sunlightWeMo%20Switch1"])
            
    

