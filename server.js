const express = require('express');
const bodyParser = require('body-parser');
const sqlite3 = require('sqlite3').verbose();
const app = require('express')();
app.set('port', process.env.PORT || 3000);
var server = app.listen(app.get('port'), function() {
  console.log('Express server listening on port ' + server.address().port);
});
module.exports = app; 

let db = new sqlite3.Database('db_games.db', (err) => {
    if (err) {
      console.error(err.message);
    }
    console.log('Connected to the database.');
  });

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
    db.all("SELECT * FROM lookup WHERE name LIKE ? COLLATE NOCASE", query ,function(err, row){
        
        if(err){
            res.render('index',{game: null, error: 'No Results Found. Please try Again!'});
            // console.log('shit err')
        }else{
            if(row == undefined){
                res.render('index',{game: null, error: 'No Results Found. Please try Again!'});
                // console.log('damn und')

            }else{
                for(let i = 0;i<row.length;i++){
                    row[i].url_name = encodeURIComponent(row[i].name)
                    // console.log(row[i].url_name)
                }
                
                res.render('index',{game: row, error: null});
            }
        }

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