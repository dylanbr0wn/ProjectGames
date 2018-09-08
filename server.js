'use strict';
const process = require('process');
const express = require('express');
const bodyParser = require('body-parser');
const Knex = require('knex');
const app = require('express')();
// app.set('port', process.env.PORT || 3000);
// var server = app.listen(app.get('port'), function() {
//   console.log('Express server listening on port ' + server.address().port);
// });
app.enable('trust proxy');

const knex = connect();

function connect () {
    const config = {
      user: process.env.SQL_USER,
      password: process.env.SQL_PASSWORD,
      database: process.env.SQL_DATABASE
    };
  
    if (process.env.INSTANCE_CONNECTION_NAME && process.env.NODE_ENV === 'production') {
      config.host = `/cloudsql/${process.env.INSTANCE_CONNECTION_NAME}`;
    }
  
    // Connect to the database
    const knex = Knex({
      client: 'pg',
      connection: config
    });
  
    return knex;
  }

app.use(express.static('public'))
app.use(bodyParser.urlencoded({ extended: true }));
app.set('view engine', 'ejs')

app.get('/', function (req, res) {
  res.render('index',{game: null, error: null})
})

app.get('/favicon.ico', (req, res) => res.status(204));

app.post('/', function (req, res) {
    let query = '%'.concat(req.body.game,'%');
    let results = []
    let gog_fail = false
    let steam_fail = false
    knex.select()
    .from('lookup')
    .where('name','ilike',query)
    .orderBy('name','desc')
    .pluck('name')
    .then(function(names){
        var urls = []
        for(let i = 0;i<names.length;i++){
            urls.push(encodeURIComponent(names[i]))
            // console.log(row[i].url_name)
        }
        res.render('index',{game: names, urls: urls,error: null});
    })
    .catch(function(error) {
        console.error(error.message)
    });
});

function getSteam(rows){

    let steam = rows[0].steam_lookup;
    // console.log(steam)
    // steam = steam.match(/\= \'(.+)\'/gi)
    if (steam.length != 0){
        // console.log('here steam')
        // steam = steam[0]
        // let steam_game = (steam.match(/(["'])(?:(?=(\\?))\2.)*?\1/gi))[0]
        // steam_game = steam_game.replace(/'/gi,'')
        // console.log(steam)
        return knex.select()
        .from('steam')
        .where('name',steam)
        .then(function(rows2){
            // console.log('where steam')
            // console.log('steam here')
            // console.log(rows[0])
            rows2[0].id = 'Steam';
            rows2[0].genre = rows2[0].genre.replace(/,/gi,', ')
            return rows2[0]
        })
        .catch(function(error) {
            console.error(error.message)
        });
    }
    return null
}


function getGOG(rows){
    let gog = rows[0].gog_lookup;
    // console.log(gog)
    // gog = gog.match(/\= \'(.+)\'/gi)
    var gog_data = null
    if (gog.length != 0){
        // gog = gog[0]
        // console.log('here gog')
        // let gog_game = (gog.match(/(["'])(?:(?=(\\?))\2.)*?\1/gi))[0]
        // gog_game = gog_game.replace(/'/gi,'')
        return knex.select()
        .from('gog')
        .where('name',gog)
        .then(function(rows2){
            rows2[0].id = 'GOG';
            rows2[0].genre = rows2[0].genre.replace(/,/gi,', ')
            // console.log(rows2[0])
            return rows2[0]
            
        }).catch(function(error) {
            console.error(error.message)
        });
    }
    return null
}


app.get('/:name', function (req, res) {
    let name = req.params['name']
    // console.log("here")
    knex.select()
    .from('lookup')
    .where('name','ilike',name)
    .then(function(rows){
        Promise.all([getGOG(rows),getSteam(rows)]).then(function(values){
            var game_data = []
            for (let i = 0;i<values.length;i++){
                if (values[i] != null){
                    game_data.push(values[i])
                }
            }
            var common = commonData(game_data)
            console.log(game_data)
            res.render('game',{game: game_data,common:common,error:null})
        })
    })
    .catch(function(error) {
        
        // console.error(error.message)
    });
    

  })




function prettyJSON(obj) {
    console.log(JSON.stringify(obj, null, 2));
}

function commonData(obj){
    var common = {}

    for(let i = 0;i<obj.length;i++){
        if(obj[i].name != null){
            if(common['name'] == null){
                common['name'] = obj[i].name;
            }
        }
        if(obj[i].developer != null){
            if(common['developer'] == null){
                common['developer'] = obj[i].developer;
            }
        }
        if(obj[i].publisher != null){
            if(common['publisher'] == null){
                common['publisher'] = obj[i].publisher;
            }
        }
        if(obj[i].release_date != null){
            if(common['release_date'] == null || common['release_date'] == '/'){
                common['release_date'] = obj[i].release_date;
            }
        }
        if(obj[i].genre != null){
            if(common['genre'] == null){
                common['genre'] = obj[i].genre;
            }
        }
    }  
    return common;
}

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`App listening on port ${PORT}`);
  console.log('Press Ctrl+C to quit.');
});

module.exports = app; 