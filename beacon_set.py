
import copy
import datetime

class BeaconSet(object):
    "A class to store beacons and stabilize the result."

    beacon_set = None
    buffer_age = None
    
    def __init__(self):
        "Inits the BeaconSet with an empty set."
        "Inits the buffer age (seconds)"
        "Starts the garbage collector script."
        self.beacon_set = []
        self.buffer_age = 20.0

    def addBeacons(self, beacons):
        "Receives an array of beacons and updates the set"
        self.beacon_set = self.beacon_set + beacons

    def getBeacons(self):
        "Produces ar array of properly averaged beacons to be submitted to the database"
        result = []
        # clone beacon_set
        beacon_set_clone = self.beacon_set[:]
        for beacon in beacon_set_clone:
            # check if it's too old. Remove if too old
            now = datetime.datetime.utcnow()
            if (now - beacon["timestamp"]).total_seconds() > self.buffer_age:
                self.beacon_set.remove(beacon)
                print "beacon_set: {0}".format(len(self.beacon_set))
                continue
            # valid beacon, insert into result
            candidate = filter(lambda final_beacon:final_beacon["major"] == beacon["major"] and final_beacon["minor"] == beacon["minor"], result)
            if len(candidate) == 0:
                beacon["count"] = 1
                result.append(beacon)
            else:
                candidate = result[result.index(candidate[0])]
                candidate["rssi"] = (candidate["rssi"] * candidate["count"] + beacon["rssi"]) / (candidate["count"] + 1)
                candidate["count"] = candidate["count"] + 1
                candidate["timestamp"] = datetime.datetime.utcnow()
        return result


