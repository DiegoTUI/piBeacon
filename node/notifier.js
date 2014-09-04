"use strict";

var Log = require("log");
var log = new Log("debug");
var apn = require("apn");
var Location = require("./location.js");

var Notifier = function(beaconsCollection) {
    // self reference
    var self = this;
    // flag to avoid notifying twice
    var notified = false;
    // id of the interval
    var intervalId;
    // location object
    var location = new Location(beaconsCollection, 513);
    // safe and danger
    var safe = require("./safe.json");
    var danger = require("./danger.json");

    self.start = function() {
        intervalId = setInterval(check, 2000);
    };

    self.stop = function() {
        clearInterval(intervalId);
    };

    function check() {
        location.getClosestPi(function (error, result) {
            if (error) return;
            log.debug("closest Pi is: " + result);
            var alert = (result === null)||(danger.indexOf(result) != -1);
            if (alert) {
                if (!notified) {
                    var message = result === null ? "Your kid died. Go get a new one." : "Your kid just entered the bar."
                    notify(message);
                }
            }
            else if (notified){
                notified = false;
            }
        });
    }

    function notify(message) {
        var options = {};
        var apnConnection = new apn.Connection(options);
        var token = "7e973adab79134fb35587ac35dd8c13b2556530b4382b7934a0ef52dfd499e9c";
        var myDevice = new apn.Device(token);
        var note = new apn.Notification();

        note.expiry = Math.floor(Date.now() / 1000) + 3600; // Expires 1 hour from now.
        note.badge = 0;
        //note.sound = "ping.aiff";
        note.alert = message;
        //note.payload = {'messageFrom': 'Caroline'};

        apnConnection.pushNotification(note, myDevice);

        notified = true;

        log.debug("Notification sent: " + message);
    }

    return self;
};

module.exports = Notifier;