const express = require('express');
const nano = require('nano')('http://admin:admin@localhost:5984');
const store = nano.db.use('db6');

get_view = async function(view_name) {

  let x = await store.view(view_name, view_name, {
    'group_level': 2,
    'reduce': true
  });

  return x['rows'];
}


module.exports = function (app) {
  app.get('/covid_sa3', function(req, res) {
    get_view("covid_sa3").then((body) => {
    // get only count of true covid tweets
    const result = body.filter(item => item['key'][1] === true);
    // make a dict!
    send_dict = {}
    result.forEach(item => {
      send_dict[item['key'][0]] = item['value'];
    });
    res.json(send_dict);
    });
  });

  app.get('/covid', function(req, res) {
    get_view("covid").then((body) => {
    // get only count of true covid tweets
    const result = body.filter(item => item['key'][1] === true);
    // make a dict!
    send_dict = {}
    result.forEach(item => {
      send_dict[item['key'][0]] = item['value'];
    });
    res.json(send_dict);
    });
  });

  app.get('/score', function(req, res) {
    get_view("score").then((body) => {
    // get only count of true covid tweets
    send_dict = {}
    body.forEach(item => {
      send_dict[item['key']] = item['value'];
    });
    res.json(send_dict);
    });
  });

  app.get('/language', function(req, res) {
    get_view("language").then((body) => {
    // get only count of true covid tweets
    send_dict = {}
    body.forEach(item => {
      send_dict[item['key']] = item['value'];
    });
      res.json(send_dict);
    });
  });




};
