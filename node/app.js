"use strict";

// requires
var MongoClient = require("mongodb").MongoClient;
var Log = require("log");
var log = new Log("debug");

// open mongo
MongoClient.connect("mongodb://127.0.0.1:27017/InnovationLab", function(error, db) {
    if(error) throw error;

    var beacons_collection = db.collection("beacons");

    setInterval(check, 2000);

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