import numpy as np
import scipy
import os
import sys
from sklearn.metrics.pairwise import cosine_similarity

debug=0
total_minutes=0

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


def getIntervals(device_min_visibility, interval, wemo):
    device_interval_visibility = {}
    for device in device_min_visibility:
        device_interval_visibility[device] = []
        total_mins = len(device_min_visibility[device])
        for current_interval in range(0, total_mins/interval):
            visible = 0
            for min_within_interval in range(0, interval):
                curr_min = current_interval*interval+min_within_interval
                visible = visible | int(device_min_visibility[device][curr_min])
                if debug:
                    print device + " min:" + str(curr_min) + " visible:" + str(visible)
            # device visiblity during in the interval
            if debug:
                print device + " interval:" + str(current_interval) + " visible" + str(visible)
            device_interval_visibility[device].append(visible)
            
    return device_interval_visibility

            
def findTransitionPointsForDevice(device_name, min_intervals_for_transition, device_interval_visibility):        
    if device_name in device_interval_visibility:
        pass
    else:
        return
        
    device_visibility_array = device_interval_visibility[device_name]
    transition_intervals = [] 
    for interval in range(0,len(device_visibility_array)):
        # check left values
        is_transition_point = True
        for prev_interval in range( interval - min_intervals_for_transition, interval):
            if prev_interval >= 0:
                if device_visibility_array[interval] == device_visibility_array[prev_interval]:
                    is_transition_point = False
                    break
            else:
                is_transition_point = False
                break
        
        # check 
        if is_transition_point == True:
            transition_intervals.append(interval)
            if debug:
                print "Transition point:" + device_name + ":" + " interval:" + str(interval) +  str(device_interval_visibility[device_name][interval-min_intervals_for_transition:interval+1])
        else:
            if debug:
                print "Not Transition point:" + device_name + ":" + " interval:" + str(interval)
    return transition_intervals
    

def OLDgetIntervals(d, interval, wemo):
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
                

    
                
def OLDwriteCosine(filename, dictionary, wemo):
    f = open(filename, "w")
    arr = []
    for w in wemo:
        for device in dictionary:
            if device != w:
                sim = cosine_similarity(dictionary[w], dictionary[device])[0][0]
                arr.append((sim, str(w) + " " + str(device) + " : " + str(sim) + "\n"))
    arr.sort(reverse=True, key=lambda x : x[0])    
    for e in arr:
        f.write(e[1])
    

def plotDeviceInterval(device_interval_visibility):
    #
    # plot graph
    #
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    plt.axis([0, max_minute_from_beginning_of_start_date, 0, len(device_visibility_for_day)+1]) # xmin, xmax, ymin, ymax

    device_number=1
    y_number=[]
    y_ticks=[]
    for device in device_interval_visibility:
        deviceName = device

        if names is not None:
            if device in names:
                deviceName =  names[device] + device

        y_number.append(device_number)
        y_ticks.append(deviceName)
        for min_of_day in range(0,max_minute_from_beginning_of_start_date):
            if device_visibility_for_day[device].get(min_of_day, 0) != 0:
                plt.scatter(min_of_day, device_number)
                # 
                # print "plt: (" + str(min_of_day) + "," + str(device_number) + ")"

        device_number = device_number+1

    plt.xlabel("Time (minute of the day) ")
    plt.yticks(y_number, y_ticks)
    # We change the fontsize of minor ticks label 
    #plt.rcParams['ytick.labelsize'] = 8
    #plt.tick_params(axis='both', which='minor', labelsize=8)
    # We change the fontsize of minor ticks label 
    plt.tick_params(axis='both', which='major', labelsize=8)
    plt.tick_params(axis='both', which='minor', labelsize=6)

    #This makes the figure's width  inches, and its height  inches.
    plt.rcParams['figure.figsize'] = 40, 10
    # adjust margins NOT WORKING
    #plt.subplots_adjust(left=100, bottom=0, right=101, top=1, wspace=0, hspace=0)
    # Tweak spacing to prevent clipping of tick-labels
    plt.subplots_adjust(left=0.25)

    plt.savefig('/tmp/daily')
    plt.close()



def writeCosine(filename, dictionary, wemo):
    arr = []
    for w in wemo:
        for device in dictionary:
            if device != w:
                sim = cosine_similarity(dictionary[w], dictionary[device])[0][0]
                #arr.append((sim, str(w) + " " + str(device) + " : " + str(sim) + "\n"))
                arr.append((sim,  str(device)))
    arr.sort(reverse=True, key=lambda x : x[0])    
    return arr

if len(sys.argv) != 3:
    print "Usage:" + sys.argv[0]  + " input_file"  + " home_id"

input_file=sys.argv[1]
home_id=sys.argv[2]

#device_visibility_by_minute = readfile("/tmp/dec2829.txt")
device_visibility_by_minute = readfile(input_file)
#setInterval(device_visibility_by_minute, 1)
interval=15
action_minute_device_dependant_device_map = {}

device_interval_visibility=getIntervals(device_visibility_by_minute, interval,["tejlightWeMo%20Insight", "sunlightWeMo%20Switch1"])

print "Device Visibility interval:" + str(interval)
for device in device_interval_visibility:
    print str(device) + ":" + str(device_interval_visibility[device])





# CHANGE 
# For teja
if home_id == "kart":
    # For kart
    device_name = "WeMo%20Switch1"
else:
    device_name = "tejlightWeMo%20Insight"

min_intervals_for_transition = 2
print str(device_interval_visibility)
transition_intervals = findTransitionPointsForDevice(device_name, 
                                                     2, #min_intervals_for_transition, 
                                                     device_interval_visibility)

print "Transition points:" + device_name
print transition_intervals

if transition_intervals is None or len(transition_intervals) == 0 :
    print "ZERO TRANSITION POINTS"
    sys.exit(0)

for transition_interval in transition_intervals:
    device_visibility_near_transition = {}
    for device in device_interval_visibility:
        device_visibility_near_transition[device] = []
        for  curr_interval in range(transition_interval-min_intervals_for_transition, transition_interval+min_intervals_for_transition):
            if (curr_interval < 0 or   curr_interval > len(device_interval_visibility[device])) :
                pass
            else:
                device_visibility_near_transition[device].append(device_interval_visibility[device][curr_interval])
    # apply algo on the intervals near transition point 
    
    device_cosine_similarity = writeCosine(device_name + "_cosine_similarity.txt", device_visibility_near_transition, [device_name])
    print "============= Cosine similariy:" + device_name + " for transition interval" + str(transition_interval)
    print "Input:"
    for device in device_visibility_near_transition:
        print " " + device + ":" + str(device_visibility_near_transition[device])

    # print device_cosine_similarity
    print "Result:"
    for entry in device_cosine_similarity:
        print " " + str(entry)
        
    device_similarity_threshold = 0.9

    for entry in device_cosine_similarity:
        device_similarity =  entry[0]
        dependant_device = entry[1]
        if device_similarity >= device_similarity_threshold:
            for  curr_interval in range(transition_interval-min_intervals_for_transition, transition_interval+min_intervals_for_transition):
                for curr_minute in range(curr_interval * interval, (curr_interval+1) * interval):
                    if curr_minute in action_minute_device_dependant_device_map:
                        pass
                    else:
                        action_minute_device_dependant_device_map[curr_minute] = {}
                        action_minute_device_dependant_device_map[curr_minute][dependant_device] = device_name


print "========================="
total_minutes= len(device_visibility_by_minute[device_visibility_by_minute.keys()[0]])
print "Every minute dependency results:  total_minutes:" + str(total_minutes)
for curr_minute in range(0, total_minutes):
    if curr_minute in action_minute_device_dependant_device_map:
        device_dependant_device_map = action_minute_device_dependant_device_map[curr_minute]
        for device in device_dependant_device_map:
            print "Interval:" + str(curr_minute/interval) + " Start Min:" + str(curr_minute) + " Hr:" + str(curr_minute/60) + " min:" + str(curr_minute%60) + " " + device  +  " " + " controls " + device_dependant_device_map[device] + " visible:" + str(int(device_visibility_by_minute[device][curr_minute]))
            print "SIMILARACTION " + str(curr_minute) + " " +  device  +  " " + device_dependant_device_map[device]
    
    

#writeCosine("cosine_similarity.txt", device_visibility_by_minute, ["tejlightWeMo%20Insight", "sunlightWeMo%20Switch1"])
            
    

