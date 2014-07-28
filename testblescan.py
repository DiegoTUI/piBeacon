# test BLE Scanning software
# jcs 6/8/2014

import blescan
import sys
import threading
import datetime

import bluetooth._bluetooth as bluez

from pymongo import MongoClient
mongo_client = MongoClient('mongodb://54.77.67.205:27017/')
db = mongo_client.InnovationLab
beacons_collection = db.beacons

pi_id = "RPi_1"

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
        beacon["pi_id"] = pi_id
        beacon["timestamp"] = datetime.datetime.utcnow()
        beacons_collection.update({"pi_id":pi_id, "udid":beacon["udid"], "major":beacon["major"], "minor":beacon["minor"]}, {"$set": beacon}, upsert=True)
    #beacons_collection.insert(beacons)
    threading.Timer(2.0, scan).start()

scan()

