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

function getlookup (knex,game){
    let query = '%'.concat(req.body.game,'%');
    return knex.select().from('lookup').where('name','ilike',query).orderBy('name',)
}


app.post('/', function (req, res) {
    let query = '%'.concat(req.body.game,'%');
    let results = []
    let gog_fail = false
    let steam_fail = false
    knex.select()
    .from('lookup')
    .where('name','ilike',query)
    .orderBy('name',)
    .pluck('name')
    .then(function(names){
        var urls = []
        for(let i = 0;i<names.length;i++){
            urls.push(encodeURIComponent(names[i]))
            // console.log(row[i].url_name)
        }
        res.render('index',{game: names, urls: urls,error: null}, { _with: false });
    })
    .catch(function(error) {
        console.error(error.message)
    });
});


app.get('/:name', function (req, res) {
    let name = req.params['name']
    // console.log(name)
    db.get("SELECT * FROM lookup WHERE name LIKE ? COLLATE NOCASE", name ,function(err, row){
        let game_stats =[]
        let steam = row.steam_lookup;
        let gog = row.gog_lookup;

        db.get(gog,function(err2,row2){
            if (err2){

                // console.log('shiiiiiiit gog')
            }else{
                // console.log('adding gog')
                row2.id = 'GOG';
                row2.genre = row2.genre.replace(/,/gi,', ')
                game_stats.push(row2)
             
            }
            db.get(steam,function(err3,row3){
                if (err3){
                    // console.log('shiiiiiiit steam')
                }else{
                    // console.log('adding steam')
                    row3.id = 'Steam';
                    row3.genre = row3.genre.replace(/,/gi,', ')
                    game_stats.push(row3)
                    
                    
                }
                var common = commonData(game_stats)
                // console.log(commonData(game_stats))
                res.render('game',{game: game_stats, common: common, error: null});
            });
        });
        
    });

  })




function prettyJSON(obj) {
    console.log(JSON.stringify(obj, null, 2));
}

function commonData(obj){
    var common = {}

    for(let i = 0;i<obj.length;i++){
        if(obj[i].name != ''){
            if(common['name'] == null){
                common['name'] = obj[i].name;
            }
        }
        if(obj[i].developer != ''){
            if(common['developer'] == null){
                common['developer'] = obj[i].developer;
            }
        }
        if(obj[i].publisher != ''){
            if(common['publisher'] == null){
                common['publisher'] = obj[i].publisher;
            }
        }
        if(obj[i].release_date != ''){
            if(common['release_date'] == null || common['release_date'] == '/'){
                common['release_date'] = obj[i].release_date;
            }
        }
        if(obj[i].genre != ''){
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