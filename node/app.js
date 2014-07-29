"use strict";

// requires
var MongoClient = require("mongodb").MongoClient;
var apn = require('apn');
var Log = require("log");
var log = new Log("debug");

// open mongo
MongoClient.connect("mongodb://127.0.0.1:27017/InnovationLab", function(error, db) {
    if(error) throw error;

    var beacons_collection = db.collection("beacons");

    // send test push notification
    log.debug("Starting notifications...");
    var options = {};
    var apnConnection = new apn.Connection(options);
    var token = "7e973adab79134fb35587ac35dd8c13b2556530b4382b7934a0ef52dfd499e9c";
    var myDevice = new apn.Device(token);
    var note = new apn.Notification();

    note.expiry = Math.floor(Date.now() / 1000) + 3600; // Expires 1 hour from now.
    note.badge = 3;
    note.sound = "ping.aiff";
    note.alert = "\uD83D\uDCE7 \u2709 You have a new message";
    note.payload = {'messageFrom': 'Caroline'};

    apnConnection.pushNotification(note, myDevice);

    log.debug("Notification sent");

    //setInterval(check, 2000);

    function check() {
        beacons_collection.findOne({minor: 513}, function (error, result) {
            if (error || !result) return;
            if (result.rssi < -90) {
                // Notify!!!
                log.error("KID FAR AWAY!!!");
            }
        });
    }
});