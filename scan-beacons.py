# test BLE Scanning software
# jcs 6/8/2014

import blescan
import sys
import threading
import datetime
import uuid
import os
import signal
from beacon_set import BeaconSet
import bluetooth._bluetooth as bluez

# init db
from pymongo import MongoClient
mongo_client = MongoClient('mongodb://54.77.67.205:27017/')
db = mongo_client.InnovationLab
beacons_collection = db.beacons

# init bluetooth
try:
    sock = bluez.hci_open_dev(0)
    print "ble thread started"
except:
    print "error accessing bluetooth device..."
    sys.exit(1)

blescan.hci_le_set_scan_parameters(sock)
blescan.hci_enable_le_scan(sock)

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

# beacons and scanning constants
UDID_estimote = "b9407f30f5f8466eaff925556b57fe6d"
UDID_guardian = "01060303d71a03194004070931323233"
UDID = UDID_guardian;
scan_period = 0.1
update_database_period = 2.0
beacon_set = BeaconSet()

def scan():
    global beacon_set
    beacons = blescan.parse_events(sock, 10)
    filtered_beacons = filter(lambda beacon:beacon["udid"] == UDID, beacons)
    for beacon in filtered_beacons:
        print "minor: {0} - tx: {1} - rssi: {2}".format(beacon["minor"], beacon["tx"], beacon["rssi"])
        # update pi_id and timestamp
        beacon["pi_id"] = pi_id
        beacon["timestamp"] = datetime.datetime.utcnow()
    beacon_set.addBeacons(filtered_beacons)
    threading.Timer(scan_period, scan).start()

def update_database():
    global beacon_set
    # print "updating database with {0} beacons".format(len(beacons_to_send))
    # clone the array of beacons to send and reset beacons_to_send
    beacons_to_send = beacon_set.getBeacons();
    for beacon in beacons_to_send:
        print "SEND -- minor: {0} - tx: {1} - rssi: {2}".format(beacon["minor"], beacon["tx"], beacon["rssi"])
        beacons_collection.update({"pi_id":pi_id, "udid":beacon["udid"], "major":beacon["major"], "minor":beacon["minor"]}, {"$set": beacon}, upsert=True)
    threading.Timer(update_database_period, update_database).start()

def on_exit():
    print "closing database"
    mongo_client.close()

# assign SIGTERM to on_exit
signal.signal(signal.SIGTERM, on_exit)

# start scanning
scan()
# start updating database
update_database()

