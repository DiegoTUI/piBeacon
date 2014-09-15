# test BLE Scanning software
# jcs 6/8/2014

import blescan
import sys
import threading
import datetime
import uuid
import os
import signal

import bluetooth._bluetooth as bluez

from pymongo import MongoClient
mongo_client = MongoClient('mongodb://54.77.67.205:27017/')
db = mongo_client.InnovationLab
beacons_collection = db.beacons

# read pi_id from file assign a random string otherwise

try:
    name_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "name.txt")
    pi_id = open(name_path).readline().rstrip("\n")
except:
    pi_id = str(uuid.uuid4())
    name_file = open(name_path, 'w+')
    name_file.write(pi_id)
    name_file.close()
else:
    if len(pi_id) == 0:
        pi_id = str(uuid.uuid4())
        name_file = open(name_path, 'w')
        name_file.write(pi_id)
        name_file.close()

UDID_estimote = "b9407f30f5f8466eaff925556b57fe6d"
UDID_guardian = "69FB532E-688E-162E-1B65-E23D3112902F"
# pick from estimote, guardian, etc..
UDID = UDID_guardian;

dev_id = 0
try:
	sock = bluez.hci_open_dev(dev_id)
	print "ble thread started"

except:
	print "error accessing bluetooth device..."
    	sys.exit(1)

blescan.hci_le_set_scan_parameters(sock)
blescan.hci_enable_le_scan(sock)

def scan():
    beacons = blescan.parse_events(sock, 10)
    filtered_beacons = filter(lambda beacon:beacon["udid"] == UDID, beacons)
    for beacon in filtered_beacons:
        beacon["pi_id"] = pi_id
        beacon["timestamp"] = datetime.datetime.utcnow()
        # only update if UDID is estimote
        beacons_collection.update({"pi_id":pi_id, "udid":beacon["udid"], "major":beacon["major"], "minor":beacon["minor"]}, {"$set": beacon}, upsert=True)
    #beacons_collection.insert(beacons)
    threading.Timer(2.0, scan).start()

def on_exit():
    print "closing database"
    mongo_client.close()

# assign SIGTERM to on_exit
signal.signal(signal.SIGTERM, on_exit)

# start scanning
scan()

