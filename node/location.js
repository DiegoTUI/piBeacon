"use strict";

var Log = require("log");
var log = new Log("debug");

var Location = function(beaconsCollection, minor) {
    // self reference
    var self = this;

    /**
     * Returns the id of the closest pi in the result of the callback.
     * Returns null in the following cases:
     *   - If there are no pis in either safe.json or danger.json
     *   - If there is no signal for any of the registered pis
     *   - If all the signals from registeres pis are too old (older than N seconds to now)
     */
    self.getClosestPi = function(callback) {
        beaconsCollection.find({minor: minor}, function (error, cursor) {
            if (error) {
                return callback(error);
            }

            var result = null;
            log.debug("******** result set to null *********");
            var minimumDistance = 99999999999;

            function processBeacon(error, beacon) {
                if (beacon === null) {
                    return callback(null, result);
                }
                var howFar = distance(beacon.rssi, beacon.tx);
                log.debug("howFar " + beacon.pi_id + ": " + howFar);
                var now = new Date();
                var howLongAgo = now.getTime() - beacon.timestamp.getTime();
                log.debug("howLongAgo " + beacon.pi_id + ": " + howLongAgo);
                if ((howFar < minimumDistance)&&( howLongAgo < 10000 )) {
                    result = beacon.pi_id;
                    minimumDistance = howFar;
                }
                log.debug("result: " + result);

                cursor.nextObject(processBeacon);
            }

            cursor.nextObject(processBeacon);
        });

    };

    function distance(rssi, tx) {
        var result = -1;
        if (rssi !== 0) {
            var ratio = rssi / tx;
            if (ratio < 1.0) {
                result = Math.pow(ratio, 10);
            }
            else {
                result = (0.89976)*Math.pow(ratio,7.7095) + 0.111;
            }
        }
        return result;
    }

    function concatenate(array1, array2) {
        if (array1) {
            if (array2) {
                return array1.concat(array2);
            }
            return array1;
        }
        return array2 ? array2 : [];
    }

    return self;
};

module.exports = Location;