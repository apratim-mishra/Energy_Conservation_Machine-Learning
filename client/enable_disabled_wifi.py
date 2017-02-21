import subprocess
import time
import datetime
import os

# to test sudo nmcli nm wifi off

print "Run me as root!!"

debug=0
while True:

    cmd="nmcli nm wifi "
    # $ nmcli nm wifi
    # WIFI      
    # enabled   
    wifi_enabled=False
    out= subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
    if debug > 0 :
        print out
    for line in  out.splitlines():
        if 'enabled' in line:
            wifi_enabled=True

    hostname = "google.com"
    response = os.system("ping -c 1 " + hostname)
    if (response == 0):
        if debug > 0:
            print "ping ok"
    else:
        if debug > 0:
            print "ping failed."

        wifi_enabled=False

    if wifi_enabled is False:
            if debug > 0:
                print "wifi_enabled:" + str(wifi_enabled)

            cmd="nmcli nm wifi off"
            out= subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
            time.sleep(1)
            cmd="nmcli nm wifi on"
            out= subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
            now = datetime.datetime.now()
            print now, "wifi enabled as it was off"

    time.sleep(30)
