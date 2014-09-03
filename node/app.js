"use strict";

// requires
var MongoClient = require("mongodb").MongoClient;
var Log = require("log");
var log = new Log("debug");
var Notifier = require("./notifier");

// open mongo
MongoClient.connect("mongodb://127.0.0.1:27017/InnovationLab", function(error, db) {
    // throw error if DB unavailable
    if(error) throw error;
    // create a notifier
    var notifier = new Notifier(db.collection("beacons"));
    // start notifier
    notifier.start();
});