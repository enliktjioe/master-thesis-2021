
var express = require('express');
var app = express();
var cors = require('cors');
//var store = require('google-play-scraper');
//var app_store = require('app-store-scraper');
var request = require('request');
var PythonShell = require('python-shell');
var bodyparser = require('body-parser');
const sqlite3 = require('sqlite3').verbose();
var math = require('mathjs');
const fs=require('fs');

app.use(cors());

var XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;

var allAppFeatures = { };
var message = {'success': false, 'reason': ''};
var combinedFeatures;

app.listen(8081);
app.set('json spaces', 2);
var modeEnum = {
	AppDescription: 1,
	AppReviews: 2
};

var data;

app.get('/', function(req, res){
res.send('API runninng on localhost:8081/');
});

let db = new sqlite3.Database('AppReviewDB.db', sqlite3.OPEN_READONLY, (err) => {
	if (err) {
	  console.error(err.message);
	}
	console.log('Connected to the AppReviews database.');
  });

const Database = require('better-sqlite3');
const db_apps = new Database('AppReviewDB.db', { verbose: console.log,readonly: true });


app.get('/authenticate', function(req, res){
	res.set('Content-Type', 'application/json');
	var userid = req.query.uid;
	var password = req.query.pwd;

	db.get("SELECT count(*) as rowCount from Users where UserID=? and Password=?", [userid,password],function(err, row){
		var size = parseInt(row["rowCount"]);
		if(size==1)
		{
			res.send({ 
				"authenticate": "true",
				"userid": userid.trim().toString()
			});
		}
		else
		{
			res.send({ 
				"authenticate": "false",
				"userid": userid.trim().toString()
			});
		}


	});
	
});



app.get('/BaseAppsInfo', function(req, res){
	res.set('Content-Type', 'application/json');
	db.all("SELECT appId,title,icon, (select COUNT(*) from AppReviews where appID=B.appId) NoOfReviews FROM BaseApps B where B.UserID=?", [req.query.uid],function(err, row){
			res.json(row);
		});
});

app.get('/BaseAppsInfoPerUser', function(req, res){
	// res.set('Content-Type', 'application/json');
	// db.all("SELECT appId,title,icon, (select COUNT(*) from AppReviews where appID=B.appId) NoOfReviews FROM BaseApps B", [],function(err, row){
	// 		res.json(row);
	// 	});
});


app.get('/Top10similarAppsInfo',function(req,res){
	var result=[];
	//#console.log(req.query.AppDescription);
	var sql="SELECT Competitor_AppID,title,icon, (SELECT COUNT(*) from AppReviews where appID==C.Competitor_AppID) as NoOfReviews from CompetitorApps C where Base_appID=? ORDER BY NoOfReviews DESC LIMIT 10";
	db.all(sql, [req.query.appId.trim()], (err, rows) => {
		if (err) {
		  console.log(err.message);
		}
		res.set('Context-Type','application/json');
		res.send(rows);
	  });
	
});

app.get('/review_summary', function (req,res) {
	res.set('Content-tpye','application/json');
	req.setTimeout(800000);
	var appIDs = req.query.ids.split(",");
	var Apps_SummarInfo={};
	for(var k=0;k<appIDs.length;k++)
	{
		var appID = appIDs[k];
		var info;
		var dict_all_reviews={};
		var lst_relevant_review_sents=[];

		if(k==0) {
			//base app info
			var sql="select title, description, icon, feature_terms from AppFeatureTerms_Desc D,BaseApps B where B.appId == D.appID and B.appId=?";
			const row = db_apps.prepare(sql).get(appID);
			var appFeatureInfo = JSON.parse(row['feature_terms']);
			base_app_info = {'title':row.title, 'icon':row.icon,"feature_terms": appFeatureInfo["feature_terms"], 'default_AppFeatures':appFeatureInfo['default_AppFeatures']};

			// get all reviews for this app
			var sql_reviews="select ReviewID,title,text_review,score,date from AppReviews WHERE appId=?";
			var rows= db_apps.prepare(sql_reviews).all(appID);
			for(var i=0;i<rows.length;i++){
				review_info = rows[i];
				dict_all_reviews[review_info.ReviewID] = {"title" : review_info.title, "text":review_info.text_review, "score": review_info.score, "date": review_info.date};
			}

			// array of review sents
			var sql_reviewSents="SELECT sent_id,sent_words,sent_stemmed_words,category,feature_terms,sentiment from AppReviewSents WHERE appId=?";
			var rows= db_apps.prepare(sql_reviewSents).all(appID);
			for(var i=0;i<rows.length;i++){
				review_sent_info = rows[i];
				dict_review_sent_info = {'sent_id': review_sent_info.sent_id, 'sent_words': review_sent_info.sent_words.split(" "), 'sent_stemmed_words':review_sent_info.sent_stemmed_words.split(" "),'category': review_sent_info.category, 'feature_terms': review_sent_info.feature_terms.split("|"), 'sentiment': review_sent_info.sentiment.toString(), "appID" : appID}
				lst_relevant_review_sents.push(dict_review_sent_info);
			}

		}
		else
		{
			//competitor app
			var sql="select title,icon,description,feature_terms from AppFeatureTerms_Desc D,CompetitorApps C where D.appID == C.Competitor_appID AND D.appID=?";
			const row = db_apps.prepare(sql).get(appID);
			var appFeatureInfo = JSON.parse(row['feature_terms']);
		
			base_app_info = {'title':row.title, 'icon':row.icon,"feature_terms": appFeatureInfo["feature_terms"], 'default_AppFeatures':appFeatureInfo['default_AppFeatures']};

			// get all reviews for the competitor app
			var sql_reviews="select ReviewID,title,text_review,score,date from AppReviews WHERE appId=?";
			var rows= db_apps.prepare(sql_reviews).all(appID);
			for(var i=0;i<rows.length;i++){
				review_info = rows[i];
				dict_all_reviews[review_info.ReviewID] = {"title" : review_info.title, "text":review_info.text_review, "score": review_info.score, "date": review_info.date};
			}

			// array of review sents
			var sql_reviewSents="SELECT sent_id,sent_words,sent_stemmed_words,category,feature_terms,sentiment from AppReviewSents WHERE appId=?";
			var rows= db_apps.prepare(sql_reviewSents).all(appID);
			for(var i=0;i<rows.length;i++){
				review_sent_info = rows[i];
				dict_review_sent_info = {'sent_id': review_sent_info.sent_id, 'sent_words': review_sent_info.sent_words.split(" "), 'sent_stemmed_words':review_sent_info.sent_stemmed_words.split(" "),'category': review_sent_info.category, 'feature_terms': review_sent_info.feature_terms.split("|"), 'sentiment': review_sent_info.sentiment.toString(), "appID" : appID}
				lst_relevant_review_sents.push(dict_review_sent_info);
			}


		}
		
		Apps_SummarInfo[appID] = {'Reviews': dict_all_reviews, 'ReviewSents' : lst_relevant_review_sents, 'appTitle' : base_app_info["title"], 'appIcon':base_app_info["icon"],'Description':base_app_info["feature_terms"],'AppFeatures': base_app_info["default_AppFeatures"],  'TotalSents': lst_relevant_review_sents.length.toString()};
	}

	res.send(Apps_SummarInfo);
	
});

// app.get('/app', function(req, res){
// 	var promises = [];
// 	var NoOfPages = parseInt(req.query.pages);
// 	for (var i = 0; i< NoOfPages; i++) {
// 		var promise = app_store.reviews({
// 			id: req.query.id,
// 			sort: app_store.sort.HELPFUL,
// 			page: i
// 			});
// 		promises.push(promise);
// 	}

// 	Promise.all(promises).then(values => { 
// 		res.set('Content-Type', 'application/json');
// 		values = [].concat.apply([], values);
// 		var reviews = {
// 			id: req.query.id,
// 			review_list: values
// 		};
// 		console.log("success");
// 		res.send(reviews);
// 	});
//  });

app.get('/app/description', function(req, res){
	res.set('Content-Type', 'application/json');
	db.get("SELECT appId,title,icon, (select COUNT(*) from AppReviews where appID=B.appId) NoOfReviews FROM BaseApps B WHERE appID=?", [req.query.appId],function(err, row){
			res.json(row);
		});
	app_store.app({id: req.query.id}).then(values => {  
		res.send({ 
			id: req.query.id,
			description: values.description
		});
	});
});

app.get('/stem_features', function (req,res) {
	res.set('Content-tpye','application/json');
	var lst_appFeatures = JSON.parse(req.query.appFeatures);

	data = {
		"appFeatures" : lst_appFeatures
	};

	var options = {
	mode : 'json'
	};


	var pyshell = new PythonShell('feature-extraction/Stem_Features.py', options);
	pyshell.send(data);

	pyshell.on('message', function (message) {
		console.log(message)
		res.send(message)
	});

	pyshell.end(function (err) {
		if (err){ console.log(err); }
		console.log("finished");
	});
	});


app.get('/appReviewsInfo', function (req,res) {
	res.set('Content-tpye','application/json');
	var appIDs = req.query.ids.split(",");
	
	Apps_SummarInfo={}
		// Read json file for this app
	for(var i=0;i<appIDs.length;i++)
	{
		var appID = appIDs[i];
		var json_file = appID.trim() + ".json";
		//console.log(json_file);
		var file_path = "feature-extraction/offline_review_dataset/Reviews/" + json_file;
		let rawdata = fs.readFileSync(file_path);  
		let AppSummaryInfo = JSON.parse(rawdata);  

		for(appID in AppSummaryInfo) {
			var lstReviews = AppSummaryInfo[appID];
			Apps_SummarInfo[appID] = lstReviews.length;
		}
	}
	
	res.send(Apps_SummarInfo);

});


function httpPromisePostAsync(theUrl, requestBody, identifier) {
	return new Promise(function(resolve, reject) { 
		request.timeout = 300000;
		request.post(theUrl, { json: JSON.stringify(requestBody) },
		    function (error, response, body) {
		        if (!error && response.statusCode == 200) {
		        	body.sentence = requestBody;
		        	body.identifier = identifier;
		            resolve(body);
		        } else {
		        	console.log(response);
		        	console.log(error);
		        	reject(Error(error));
		        }
		    }
		);
	});
}

function httpPostAsync(theUrl, requestBody, callback) {
	request.timeout = 30000;
	request.post(theUrl, { json: JSON.stringify(requestBody) },
	    function (error, response, body) {
	        if (!error && response.statusCode == 200) {
	        	var r = response;
	        	r.sentence = requestBody;
	            callback(r);
	        } else {
	        	console.log(response);
	        	console.log(error);
	        	reject(Error(error));
	        }
	    }
	);
}

function sendFailure(res, reason) {
	res.set('Content-Type', 'application/json');
	message.success = false;
	message.reason = reason;
	res.send(message);
}


app.get("/app/name" , function(req, res) {  
	res.set('Content-Type', 'application/json');
	app_store.app({id: parseInt(req.query.id)}).then(values => {  
		
		res.send({ 
			id: req.query.id,
			description: values.title
		});
	});
});

console.log('Server running at localhost:8081/');




