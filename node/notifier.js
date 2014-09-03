"use strict";

var Log = require("log");
var log = new Log("debug");
var apn = require("apn");

var Notifier = function(beaconsCollection) {
    // self reference
    var self = this;
    // flag to avoid notifying twice
    var notified = false;
    // id of the interval
    var intervalId;

    self.start = function() {
        intervalId = setInterval(check, 2000);
    };

    self.stop = function() {
        clearInterval(intervalId);
    };

    function check() {
        log.debug("checking...");
        beaconsCollection.findOne({minor: 513}, function (error, result) {
            if (error || !result) return;
            var alert = checkTime(result) || checkDistance(result);
            var shouldNotify = alert && !notified;
            if (shouldNotify) {
                log.debug("before notifying: " + notified);
                notify();
                log.debug("after notifying: " + notified);
            }
            else {
                log.debug("No need to notify. Setting notified to false.");
                notified = false;
            }
        });
    }

    function checkTime(beacon) {
        var now = new Date();
        var timeDifferenceMS = now.getTime() - beacon.timestamp.getTime();
        if (timeDifferenceMS > 5000) {
            log.debug ("Time alert!!: " + timeDifferenceMS);
            return true;
        }
        return false;
    }

    function checkDistance(beacon) {
        var howFar = distance(beacon.rssi, beacon.tx);
        if (howFar > 5) {
            log.debug ("Distance alert!!: " + howFar);
            return true;
        }
        return false;

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
    }

    function notify() {
        var options = {};
        var apnConnection = new apn.Connection(options);
        var token = "7e973adab79134fb35587ac35dd8c13b2556530b4382b7934a0ef52dfd499e9c";
        var myDevice = new apn.Device(token);
        var note = new apn.Notification();

        note.expiry = Math.floor(Date.now() / 1000) + 3600; // Expires 1 hour from now.
        note.badge = 0;
        //note.sound = "ping.aiff";
        note.alert = "Your kid died. Go get a new one.";
        //note.payload = {'messageFrom': 'Caroline'};

        apnConnection.pushNotification(note, myDevice);

        notified = true;

        log.debug("Notification sent");
    }
};

module.exports = Notifier;