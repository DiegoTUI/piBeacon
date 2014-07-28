# test BLE Scanning software
# jcs 6/8/2014

import blescan
import sys
import threading

import bluetooth._bluetooth as bluez

from pymongo import MongoClient
mongo_client = MongoClient('mongodb://54.77.67.205:27017/')
db = mongo_client.InnovationLab
beacons_collection = db.beacons

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
    for beacon in beacons:
        beacons_collection.remove({"udid":beacon["udid"], "major":beacon["major"], "minor":beacon["minor"]})
        beacons_collection.insert(beacon)
    #beacons_collection.insert(beacons)
    threading.Timer(2.0, scan).start()

scan()

