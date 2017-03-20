"""
Find the similar devices using Cosine Similarity
By Tejasvi Kothapalli
"""
import numpy as np
import scipy
import os
import sys
from sklearn.metrics.pairwise import cosine_similarity

debug=0
total_minutes=0

"""
Read the file and split lines by "," and return the array.

"""
def readfile(filename):
    f = open(filename, 'r')
    lines = f.readlines()
    d = {}
    for l in lines:
        elems = l.split(',')
        d[elems[0].strip()] = map(float, np.array(elems[1:]))

    return d


"""

Returns Visibility of a devices for interval of 15 mins.
Example:
Device Visibility interval:15
Phone Self64:BC:0C:67:97:BC:[1, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
Laptop ML192_168_1_137:[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
"""
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


"""
Returns the Transitions points for device_name

Transition points:tejlightWeMo%20Insight
[26, 31, 53, 56]

"""
            
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
    

"""
Finds the cosine similary of the wemo with other devices
"""
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


device_visibility_by_minute = readfile(input_file)

""" Interval for device visibility : 15 mins"""
interval=15
action_minute_device_dependant_device_map = {}

""" List of wemo device names  """
device_interval_visibility=getIntervals(device_visibility_by_minute, interval,["tejlightWeMo%20Insight", "sunlightWeMo%20Switch1"])

print "Device Visibility interval:" + str(interval)
for device in device_interval_visibility:
    print str(device) + ":" + str(device_interval_visibility[device])


# TODO: Make this generic for any home
# For teja
if home_id == "kart":
    # For kart
    device_name = "WeMo%20Switch1"
else:
    device_name = "tejlightWeMo%20Insight"


"""
Prints  the Transitions points for device_name

Transition points:tejlightWeMo%20Insight
[26, 31, 53, 56]
"""
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

'''
Apply Cosine similarity algorithm on the intervals near transition point 
Example
============= Cosine similariy:tejlightWeMo%20Insight for transition interval61
Input:
Laptop MotherB8:8D:12:08:6E:98:[0, 0, 0, 1]
Phone Self64:BC:0C:67:97:BC:[0, 0, 1, 1]
Laptop ML192_168_1_137:[1, 1, 1, 1]
Router192_168_1_1:[0, 0, 0, 0]
SmartplugC0:56:27:B4:A5:79:[1, 1, 1, 1]
TV Father00:6B:9E:4A:42:83:[0, 0, 0, 0]
Phone Father94:94:26:95:12:0B:[1, 1, 1, 1]
RouterC0:C1:C0:B2:BE:C4:[1, 1, 1, 1]
Tablet FatherC8:EB:8B:96:B6:34:[0, 0, 0, 0]
192_168_1_139:[0, 0, 0, 0]
Laptop SelfB8:E8:56:43:49:08:[0, 0, 1, 1]
Phone Mother00:BB:3A:11:E7:D5:[0, 1, 1, 1]
Chromecast6C:AD:F8:2B:AA:8D:[1, 1, 1, 1]
tejlightWeMo%20Insight:[0, 0, 1, 1]
Laptop FatherAC:BC:32:B4:01:27:[0, 0, 0, 0]
Disk80:56:F2:59:85:E2:[0, 0, 0, 0]
Result:
(0.99999999999999978, 'Phone Self64:BC:0C:67:97:BC')
(0.99999999999999978, 'Laptop SelfB8:E8:56:43:49:08')
(0.81649658092772603, 'Phone Mother00:BB:3A:11:E7:D5')
(0.70710678118654746, 'Laptop MotherB8:8D:12:08:6E:98')
(0.70710678118654746, 'Laptop ML192_168_1_137')
(0.70710678118654746, 'SmartplugC0:56:27:B4:A5:79')
(0.70710678118654746, 'Phone Father94:94:26:95:12:0B')
(0.70710678118654746, 'RouterC0:C1:C0:B2:BE:C4')
(0.70710678118654746, 'Chromecast6C:AD:F8:2B:AA:8D')
(0.0, 'Router192_168_1_1')
(0.0, 'TV Father00:6B:9E:4A:42:83')
(0.0, 'Tablet FatherC8:EB:8B:96:B6:34')
(0.0, '192_168_1_139')
(0.0, 'Laptop FatherAC:BC:32:B4:01:27')
(0.0, 'Disk80:56:F2:59:85:E2')
'''


for transition_interval in transition_intervals:
    device_visibility_near_transition = {}
    for device in device_interval_visibility:
        device_visibility_near_transition[device] = []
        for  curr_interval in range(transition_interval-min_intervals_for_transition, transition_interval+min_intervals_for_transition):
            if (curr_interval < 0 or   curr_interval > len(device_interval_visibility[device])) :
                pass
            else:
                device_visibility_near_transition[device].append(device_interval_visibility[device][curr_interval])

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




            
    

