const express = require('express');
const path = require('path');
const app = express();
const port = 3000;
const request = require('request');
const fs = require('fs');

//var json = require('./geojson/sa2_geojson.geojson');



// couch
const nano = require('nano')('http://admin:1234@115.146.95.50:5984'); // NOTE: change this.
const store = nano.db.use('db6');

app.use('/static', express.static(path.join(__dirname, 'public')))


//----------------------------------- Couch view calls ----------------------------------------

// NOTE: I'm not sure where to put these calls to make sure they're called when the user refreshes/rqeuests the site.
// Example call: db.view(designname, viewname, [params], [callback]);

let sa2_file_path = 'public/json/sa2_2.geojson'; // NOTE: sa2_2.geojson and sa3_2.geojson are only for tesing purposes.
let sa3_file_path = 'public/json/sa3_2.geojson';

async function get_views() {

    // Update covid_sa3 counts.

    await store.view('covid_sa3', 'covid_sa3', {
        'group_level': 1,
        'reduce': true
        }).then((body) => {

        // Read and parse geojson file.

        let rawdata = fs.readFileSync(sa3_file_path);
        let mapdata = JSON.parse(rawdata);

        // Update the measure values.

        for (feature of mapdata.features) {
            let measure = body.rows.find(doc => doc.key[0] === feature.properties.area);
            if (measure == null) {
                feature.properties.covid_tweets = 0;
            }
            else {
                feature.properties.covid_tweets = measure.value;
            }
        }

        // Write updated data into geojson file.

        let inputdata = JSON.stringify(mapdata);
        fs.writeFileSync(sa3_file_path, inputdata);
        console.log("COVID tweet count for sa3 update complete.");
    });

    // Update covid counts.

    await store.view('covid', 'covid', {
        'group_level': 1,
        'reduce': true
        }).then((body) => {

        // Read and parse geojson file.

        let rawdata = fs.readFileSync(sa2_file_path);
        let mapdata = JSON.parse(rawdata);

        // Update the measure values.

        for (feature of mapdata.features) {
            let measure = body.rows.find(doc => doc.key[0] === feature.properties.area);
            if (measure == null) {
                feature.properties.covid_tweets = 0;
            }
            else {
                feature.properties.covid_tweets = measure.value;
            }
        }

        // Write updated data into geojson file.

        let inputdata = JSON.stringify(mapdata);
        fs.writeFileSync(sa2_file_path, inputdata);
        console.log("COVID tweet count for sa2 update complete.");
    });

    // Update non-english tweet counts.

    await store.view('language', 'language', {
        'group_level': 1,
        'reduce': true
        }).then((body) => {

        // Read and parse geojson file.

        let rawdata = fs.readFileSync(sa2_file_path);
        let mapdata = JSON.parse(rawdata);

        // Update the measure values.

        for (feature of mapdata.features) {
            let measure = body.rows.find(doc => doc.key === feature.properties.area);
            if (measure == null) {
                feature.properties.non_english_tweets = 0;
            }
            else {
                feature.properties.non_english_tweets = measure.value;
            }
        }

        // Write updated data into geojson file.

        let inputdata = JSON.stringify(mapdata);
        fs.writeFileSync(sa2_file_path, inputdata);
        console.log("Non-english tweet count update complete.");
    });

    // Update sentiment scores (This one may take a while).

    const response = await store.view('score', 'score', {
        'group_level': 1,
        'reduce': true
        }).then((body) => {

        // Read and parse geojson file.

        let rawdata = fs.readFileSync(sa2_file_path);
        let mapdata = JSON.parse(rawdata);

        // Update the measure values.

        for (feature of mapdata.features) {
            let measure = body.rows.find(doc => doc.key === feature.properties.area); // different for each view
            if (measure == null) {
                feature.properties.sentiment_score = 0;
            }
            else {
                feature.properties.sentiment_score = measure.value;
            }
        }

        // Write updated data into geojson file.

        let inputdata = JSON.stringify(mapdata);
        fs.writeFileSync(sa2_file_path, inputdata);
        console.log("Sentiment score update complete.");
    });

    return response;
}

get_views().then(console.log);

//---------------------------------------------------------------------------------------------





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
