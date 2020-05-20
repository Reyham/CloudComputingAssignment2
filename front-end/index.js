const express = require('express');
const path = require('path');
const app = express();
const port = 3000;
const request = require('request');


// couch
const nano = require('nano')('http://admin:1234@localhost:5984');
const store = nano.db.use('db6');

app.get('/', function(req, res) {
    res.sendFile(path.join(__dirname + '/public/index.html'));
});

app.get('/getelectiondata', function(req, res){
    
});


app.listen(port, () => console.log(`Example app listening at http://localhost:${port}`));


// test route
