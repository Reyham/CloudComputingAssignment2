const express = require('express');
const path = require('path');
const app = express();
const port = 3000;
const request = require('request');
const fs = require('fs');

// routes for couchdb
require('./utils/couch_routes')(app);


app.use('/static', express.static(path.join(__dirname, 'public')))



// Home
app.get('/', function(req, res) {
    res.sendFile(path.join(__dirname + '/public/scenario2.html'));
});

// Routes for data pages
app.get('/scenario1', function(req, res) {
    res.sendFile(path.join(__dirname + '/public/scenario1.html'));
});

app.get('/scenario2', function(req, res) {
    res.sendFile(path.join(__dirname + '/public/scenario2.html'));
});


app.get('/scenario3', function(req, res) {
    res.sendFile(path.join(__dirname + '/public/scenario3.html'));
});


app.get('/scenario4', function(req, res) {
    res.sendFile(path.join(__dirname + '/public/scenario4.html'));
});


app.get('/hello', function(req, res) {
    res.send("hello world");
});



app.listen(port, () => console.log(`Example app listening at http://localhost:${port}`));


// test route
