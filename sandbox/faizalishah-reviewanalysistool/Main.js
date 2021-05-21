var categories;
var applications;
var seachedApplications;
var API_URL = "http://52.14.13.224:8081/";

var appTitles={};
var appIcons={};
var searchTerm="A";
var sentSortOrder= "asc";
var ReviewSummaryData={};
var totalReviewSents=0;
var sendDate;
var receiveDate;
//var feature_loaded=false;
var AppsSummaryInfo_plots={};
var selectedAppsOffline=[];
var List_AppFeatures=[];
var List_AppFeatures_Description=[];
var all_review_data_loaded=false;
var all_apps_review_sents=[];
var FeatureWiseAppSummarInfo_eval={};
var FeatureWiseAppSummarInfo_bugs={};
var FeatureWiseAppSummarInfo_requests={};
var all_review_data_searched = false;
var clicked_appID="";
var clicked_appFeature="";
var lst_SAFE_extracted_features_request=[];
var lst_SAFE_extracted_features_eval=[];
var lst_SAFE_extracted_features_bug=[];
var featureRequestsSentCount={};
var featureEvaluationSentCount={};
var featureBugsSentCount={};
var popup_msg="";
var lst_extracted_features_eval=[];
var lst_extracted_features_bug=[];
var lst_extracted_features_request=[];

var dict_colors = {
	"-2": "#ff0000",
	"-1":  "#ff8c00 ",
	"0" : "#663399",
	"1" : "#32CD32",
	"2" : "#006400"
};

var dict_sentimentLabels = {
	"-2": "very negative",
	"-1":  "negative",
	"0" : "neutral",
	"1" : "positive",
	"2" : "very positive"
};


function httpGetAsync(theUrl, callback) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
		if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
			$("#wait").css("display", "none");
			receiveDate = (new Date()).getTime();
			var responseTimeMs = receiveDate - sendDate;
			//var response_time_secs = responseTimeMs/10000.0;
			//console.log('Responese Time (HH:MM:SS) ->' + msToTime(responseTimeMs));
            callback(xmlHttp.responseText);
	}
	$("#wait").css("display", "block");
	sendDate = (new Date()).getTime();
    xmlHttp.open("GET", theUrl, true); 
    xmlHttp.send(null);
}

function msToTime(duration) {
    var milliseconds = parseInt((duration%1000)/100)
        , seconds = parseInt((duration/1000)%60)
        , minutes = parseInt((duration/(1000*60))%60)
        , hours = parseInt((duration/(1000*60*60))%24);

    hours = (hours < 10) ? "0" + hours : hours;
    minutes = (minutes < 10) ? "0" + minutes : minutes;
    seconds = (seconds < 10) ? "0" + seconds : seconds;

    return hours + ":" + minutes + ":" + seconds + "." + milliseconds;
}

function httpPostAsync(theUrl, body, callback) {
	var xhr = new XMLHttpRequest();
	var url = theUrl;
	xhr.open("POST", url, true);
	xhr.setRequestHeader("Content-type", "application/json");
	xhr.onreadystatechange = function () {
    	if (xhr.readyState === 4 && xhr.status === 200) {
        	var json = JSON.parse(xhr.responseText);
        	callback(json);
    	}
	};
	var data = JSON.stringify(body);
	xhr.send(data);
}


var checkedApplicationsCheckboxes = {};
var checkedmainApplication = [];
function addOnRadioClick(element, uncheck = true) {
	element.onclick =  function () {
		//unchecking the checked checkbox
		if (element.checked != true) {
    		checkedmainApplication=[];
			element.checked = false; 
			//addAboveCategories();
			return;
		}

		//checkedApplicationsCheckboxes[element.id] = {};
		checkedmainApplication=[];
		//checkedApplicationsCheckboxes[element.id].title = element.name;
		checkedmainApplication.push(element.id);
		
		loadSimilarApps();
		//addAboveCategories();
	
		element.checked = true;
	};
}

function addOnClick(element, uncheck = true,addAboveCategories = function(){}) {
	element.onclick =  function () {
		//unchecking the checked checkbox
		if (element.checked != true) {
			delete checkedApplicationsCheckboxes[element.id];
			element.checked = false; 
			addAboveCategories();
			return;
		}

		checkedApplicationsCheckboxes[element.id] = {};
		checkedApplicationsCheckboxes[element.id].title = element.name;
		
		addAboveCategories();
	
		element.checked = true;
	};
}


function getUrlVars() {
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for(var i = 0; i < hashes.length; i++)
    {
        hash = hashes[i].split('=');
        vars.push(hash[0]);
        vars[hash[0]] = hash[1];
    }
    return vars;
}

function clearLines(container) {
	var elementsToRemove = [];
   	for (var i = 0; i < container.children.length; i++) {
      var e = container.children[i];
      if (e.id == 'line') { 
      	elementsToRemove.push(e);
      }
  	}

  	for (e in elementsToRemove) {
  		container.removeChild(elementsToRemove[e]);
  	}
}

function clearElements(container, elementName) {
	var elementsToRemove = [];
   	for (var i = 0; i < container.children.length; i++) {
      var e = container.children[i];
      if (e.id == elementName) { 
      	elementsToRemove.push(e);
      }
  	}

  	for (e in elementsToRemove) {
  		container.removeChild(elementsToRemove[e]);
  	}
}

function line() {
	var line = document.createElement('hr');
	line.setAttribute('id','line');

	return line;
}


function createLabel(text, divId, textColor) {
	var div = document.createElement('div');
	if (divId !== undefined) { div.setAttribute('id', divId); } 
	
    var label = document.createElement('label');
    label.innerHTML = text;

    if (textColor !== undefined) { label.style.color = textColor; }
    
    div.appendChild(label);
    return div;
}

function buttonLoading() {
    $("#next-button").button('loading');
}

function buttonReset() {
	$("#next-button").button('reset');
}

var searchDelay = (function(){
  var timer = 0;
  return function(callback, ms){
    clearTimeout (timer);
    timer = setTimeout(callback, ms);
  };
})();

//* Categories methods *//
function loadCategories() {
	httpGetAsync(API_URL + "categories", extractCategories);
};

function getAppInfo(appid) {
	httpGetAsync(API_URL + "appInfo?id=" + appid, RetriveAppTitle);
}

function RetriveAppTitle(responseText)  {
	appTitles.push(JSON.parse(responseText)['title']);	
}

var data_loaded=false;

function getReviewsSummary() {
	//PopulateAppsList();

	var selectedReviewmode= getUrlVars()["mode"];

	if(selectedReviewmode=="live")
	{
		var NumReviews = document.getElementById("txtNumReviews");
		NoOfReviews = parseInt(getUrlVars()['reviews']);
		NoOfPages = Math.round(NoOfReviews/40);
		api_location = API_URL + "review_summary";
		//query string data
		api_location += "?ids=" + getUrlVars()["ids"] + "&pages=" + NoOfPages + "&mode=" + selectedReviewmode;
		// call rest API
		data_loaded = true;
		httpGetAsync(api_location, ExtractSummary);
	}
	else if (selectedReviewmode=="offline")
	{
		api_location = API_URL + "review_summary";
		//query string data
		api_location += "?ids=" + getUrlVars()["ids"] + "&mode=" + selectedReviewmode;
		// call rest API
		data_loaded = true;
		httpGetAsync(api_location, ExtractSummary);
	}
	
}

function categorySearchChange() {
	searchDelay(function(){
      var searchString = document.getElementById('srch-term').value;
		if (searchString !== "") {
			httpGetAsync(API_URL + "searchApp?searchString=" + document.getElementById('srch-term').value, applicationSearchByName);
		}
    }, 250 );
}

function applicationSearchByName(responseText) {
	this.seachedApplications = JSON.parse(responseText);
	drawApplicationsAboveTheCategories(this.seachedApplications);
}


function addChosenAppsAboveCategories() {
	// var chosenAppsDiv = document.getElementById("chosen-apps-div");
	// chosenAppsDiv.innerHTML = "";

	var nextButton = document.getElementById("next-button");
	//var NumReviewsDiv = document.getElementById("NumReviews");

	
	if (Object.keys(checkedApplicationsCheckboxes).length <1)
		{
			nextButton.disabled = true;
			//NumReviewsDiv.style.display = "none";
		}
		else
		{
			nextButton.disabled = false;
			//NumReviewsDiv.style.display = "block";
		}

	//console.log(checkedApplicationsCheckboxes.length)

	// if (Object.keys(checkedApplicationsCheckboxes).length > 0) {
	// 	var title = createBoldLabel("Choose app(s) from the following list of similar apps:", '#208c22', 15);
	// 	title.style.marginTop = "15px";
	// 	chosenAppsDiv.appendChild(title);

	// 	for (var k in checkedApplicationsCheckboxes) {
	// 	    var label = document.createElement('label');
	// 	    label.innerHTML = checkedApplicationsCheckboxes[k].title;
		
	// 		var div = document.createElement('div');
	// 		div.setAttribute('class','radio');
	// 		div.setAttribute('id','radio-div');

	// 		div.appendChild(label);
	// 		chosenAppsDiv.appendChild(div);	
	//     } 
	//     chosenAppsDiv.appendChild(line());
	// }	
}

function MainAppChanged()
{
	loadSimilarApps();
}

function loadSimilarApps() {
	var main_app = document.getElementById("main_apps").value;
	// var url = API_URL + "similarApps?id=" + $("input[name=mainApp]:checked").val();
	var url = API_URL + "similarApps?id=" + main_app;
	httpGetAsync(url, getSimilarApps);
};

function getSimilarApps(responseText) {
	var similarApplications = JSON.parse(responseText);
	//console.log(similarApplications);
	drawSimilarApplications(similarApplications);
}

function drawSimilarApplications(similarApplications)
{
	var NumOfApps=0;

	if(similarApplications.length>25)
		NumOfApps = 25;
	else
		NumOfApps = similarApplications.length;
	
	var similarAppsDiv = document.getElementById("similar-apps-div");
	similarAppsDiv.innerHTML = "";

	var nextButton = document.getElementById("next-button");
	//var NumReviewsDiv = document.getElementById("NumReviews");
	
	// if (Object.keys(checkedApplicationsCheckboxes).length < 2)
	// 	{
	// 		nextButton.disabled = true;
	// 		NumReviewsDiv.style.display = "none";
	// 	}
	// 	else
	// 	{
	// 		nextButton.disabled = false;
	// 		NumReviewsDiv.style.display = "block";
	// 	}

	//console.log(checkedApplicationsCheckboxes.length)

	// if (checkedmainApplication.length == 1) {
	var title = createBoldLabel("You can select app(s) from the following list of apps for comparison:", '#208c22', 15);
	title.style.marginTop = "15px";
	similarAppsDiv.appendChild(title);

	var count=0;

	for (var k in similarApplications) {

		var input = document.createElement("input");
		input.type = "checkbox";
		input.name = similarApplications[k].title;
		input.id = similarApplications[k].id;
		addOnClick(input, uncheck = false,addChosenAppsAboveCategories);
		if (Object.keys(checkedApplicationsCheckboxes).indexOf(input.id) != -1) {
			input.checked = true;
		}

		var label = document.createElement('label');
		label.setAttribute("for", input);
		label.innerHTML = similarApplications[k].title;
		label.setAttribute('style','margin-left:2px;font-weight:normal;font-size:13px;');
	
		var div = document.createElement('div');
		div.setAttribute('style','margin-left:10px;float:left;');
		//div.setAttribute('class','radio');
		//div.setAttribute('id','radio-div');

		div.appendChild(input);
		div.appendChild(label);
		similarAppsDiv.appendChild(div);	

		// var label = document.createElement('label');
		// label.innerHTML = similarApplications[k].title;
	
		// var div = document.createElement('div');
		// div.setAttribute('class','radio');
		// div.setAttribute('id','radio-div');

		// div.appendChild(label);
		// similarAppsDiv.appendChild(div);	

		count = count + 1;

		if(count==NumOfApps)
			break;
		// } 
		var div = document.createElement('div');
			div.setAttribute('style','clear:left;');
		similarAppsDiv.appendChild(div);
	    //similarAppsDiv.appendChild(line());
	}	
}



function drawApplicationsAboveTheCategories(applications) {
	//console.log(applications)
	var searchedAppDiv = document.getElementById("main-apps-div");
	searchedAppDiv.innerHTML = "";
	if (applications.length > 0) {
		var title = createBoldLabel("Please choose the main application", '#9A3334', 15);
		title.style.marginTop = "15px";
		searchedAppDiv.appendChild(title);

		for (var k in applications) {
			var input = document.createElement("input");
		    input.type = "radio";
			input.name = "mainApp";
			input.value = applications[k].id;
			input.id = applications[k].id;
		    addOnRadioClick(input, uncheck = false);
		    // if (Object.keys(checkedApplicationsCheckboxes).indexOf(input.id) != -1) {
		    // 	input.checked = true;
		    // }

		    var label = document.createElement('label');
		    label.setAttribute("for", input);
			label.innerHTML = applications[k].title;
			label.setAttribute('style','margin-left:10px;font-weight:normal;font-size:13px;');
		
			var div = document.createElement('div');
			//div.setAttribute('class','radio');
			div.setAttribute('style','margin-left:5px');
			//div.setAttribute('id','radio-div');

			div.appendChild(input);
			div.appendChild(label);
			searchedAppDiv.appendChild(div);	
	    } 
	    searchedAppDiv.appendChild(line());
	}	
}


function ExtractSummary(responseText) {
	ReviewSummaryData = JSON.parse(responseText);
	ShowReviewSummary(ReviewSummaryData);
	//ShowChart();
}

function AppChanged(){
 	var selectedApp = document.getElementById("filterbyApp").value;
 	var sentCategory = document.getElementById("filterbySentType").value;
 	var polarity_range = [$("#slider-range" ).slider("values", 0 ), $( "#slider-range" ).slider( "values",1) ];
 	ShowReviewSummary(ReviewSummaryData,polarity_range,selectedApp,sentCategory);
}

var sort_by = function(field, reverse, primer){

	var key = primer ? 
		function(x) {return primer(x[field])} : 
		function(x) {return x[field]};
 
	reverse = !reverse ? 1 : -1;
 
	return function (a, b) {
		return a = key(a), b = key(b), reverse * ((a > b) - (b > a));
	  } 
 }

 function DisplayMsg() {
	 alert('This fuctionality is only valid for sentencec types: feature evalation and bug report')
 }

 function setSliderValue(val) {
	var slider = document.getElementById("frequency_range");
	slider.value = val;
	var output = document.getElementById("frequency_value");
	output.innerHTML = slider.value;
 }

function SentTypeChanged() {
	
	//if(elem.checked==true)

	var sentCategory = document.getElementById("filterbySentType").value;
	var selectedReviewmode= getUrlVars()["mode"];
	var feature_extraction_approach = document.getElementById("lstExtractionApproach").value;
	
	//alert(sentCategory);

	if(sentCategory=="R" && selectedReviewmode=="offline") {
		setSliderValue(2);
		//document.getElementById('lnkModify').onclick = DisplayMsg();
	}
	else if(sentCategory=="R" && selectedReviewmode=="live")
	{
		setSliderValue(1);
	}
	else if(sentCategory=="E" && selectedReviewmode=="offline") {
		if(feature_extraction_approach=="ONE_WORD_NOUN")
			setSliderValue(50);
		else if (feature_extraction_approach=="SAFE")
			setSliderValue(10);
	}
	else if(sentCategory=="E" && selectedReviewmode=="live") {
		setSliderValue(1);
	}
	else if(sentCategory=="B" && selectedReviewmode=="offline") {
		if(feature_extraction_approach=="ONE_WORD_NOUN")
			setSliderValue(25);
		else if (feature_extraction_approach=="SAFE")
			setSliderValue(2);
	}
	else if(sentCategory=="B" && selectedReviewmode=="live") {
		setSliderValue(2);
	}

	updateSummaryInfo();


	// var selectedApp = document.getElementById("filterbyApp").value;
	// var sentCategory = document.getElementById("filterbySentType").value;
	// var polarity_range = [$("#slider-range" ).slider("values", 0 ), $( "#slider-range" ).slider( "values",1) ];

	// if (sentCategory=='B' || sentCategory=='R')
	// {
	// 	var divSort = document.getElementById("divSort");
	// 	divSort.style.display = "none";

	// 	$('#slider-range').slider( 'disable');
	// }
	// else if (sentCategory=='E' || sentCategory=="A")
	// {
	// 	$('#slider-range').slider('enable');

	// 	$("#slider-range").slider('values',0,0);
	// 	$("#slider-range").slider('values',1,4);

	// 	var divSort = document.getElementById("divSort");
	// 	var btnSort = document.getElementById("btnSort");
	// 	divSort.style.display = "block";
	// 	btnSort.className = "triangle-down";
	// 	sort();
	// }
	 
 	// ShowReviewSummary(ReviewSummaryData,polarity_range,selectedApp,sentCategory);
}

function onlyUnique(value, index, self) { 
    return self.indexOf(value) === index;
}

function sort()
{
	//alert('sort sents with +ve sentiments on top');
	divSort = document.getElementById("btnSort");
	if (divSort.className == "triangle-up")
	{
		divSort.className = "triangle-down";
		sentSortOrder= "desc";
	}
	else
	{
		divSort.className = "triangle-up";
		sentSortOrder= "asc";
	}

	//var selectedApp = document.getElementById("filterbyApp").value;
	//var sentCategory = document.getElementById("filterbySentType").value;
	//var polarity_range = [$("#slider-range" ).slider("values", 0 ), $( "#slider-range" ).slider( "values",1) ];
	//ShowReviewSummary(ReviewSummaryData,polarity_range,selectedApp,sentCategory);
	ShowReviewSentencesAgainstSelectedAppFeature_App(clicked_appID,clicked_appFeature,"E");

}

function getSelectedSentenceType()
{

	//var selectedsentType=[];
	// var eval = document.getElementById('E')
	// var bug = document.getElementById('B')
	// var requests = document.getElementById('R')

	// if(eval.checked)
	// 	selectedsentTypes.push('E');
	
	// if(bug.checked)
	// 	selectedsentTypes.push('B');
	
	// if(requests.checked)
	// 	selectedsentTypes.push('R');
	

	var sentType = document.getElementById("filterbySentType").value;

	return sentType;


	return selectedsentTypes;

}


function ShowReviewSummary(SummaryInfo){

	showFrequencySlider();

	var appIds = getUrlVars()["ids"].split(',');
	var app_feature_source=$('input[name=AppFeature_Source]:checked').val();
	var selected_sentCatgory = getSelectedSentenceType();
	
	if(all_review_data_loaded==false) {
		totalReviewSents=0;
		for (var i = 0; i < appIds.length; i++) {
			var ReviewSentsInfo = SummaryInfo[appIds[i]]['ReviewSents'];

			var count_Evals=0, count_Requests=0, count_bugs=0, sum_eval_sentiment_score=0;
			
			for(var j=0;j<ReviewSentsInfo.length;j++)
			{
				var sentCategory = ReviewSentsInfo[j]['category'];

				if(sentCategory=="E") {
					count_Evals = count_Evals + 1;
					var safe_extracted_features = ReviewSentsInfo[j]['feature_terms'];
					sum_eval_sentiment_score = sum_eval_sentiment_score + parseInt(ReviewSentsInfo[j]['sentiment'])
					lst_SAFE_extracted_features_eval = lst_SAFE_extracted_features_eval.concat(safe_extracted_features);
				}
				else if (sentCategory=="R") {
					var safe_extracted_features = ReviewSentsInfo[j]['feature_terms'];
					lst_SAFE_extracted_features_request = lst_SAFE_extracted_features_request.concat(safe_extracted_features);
					count_Requests = count_Requests + 1;
				}
				else if (sentCategory == "B")
				{
					var safe_extracted_features = ReviewSentsInfo[j]['feature_terms'];
					lst_SAFE_extracted_features_bug = lst_SAFE_extracted_features_bug.concat(safe_extracted_features);
					count_bugs = count_bugs + 1;
				}

				var sentiment_score = ReviewSentsInfo[j]['sentiment'];
			}

			//set list of SAFE extracted features from app description as default app feautres
			var lstAppFeatures_default = SummaryInfo[appIds[i]]['AppFeatures'];

			List_AppFeatures_Description = List_AppFeatures_Description.concat(lstAppFeatures_default)

			totalReviewSents = totalReviewSents + parseInt(SummaryInfo[appIds[i]]['TotalSents']);
			var app_title = SummaryInfo[appIds[i]]['appTitle'];
			app_title = app_title.replace(/\u2013|\u2014/g, "-");
			app_title = app_title.replace("-"," ");
			var appWords = app_title.split(" ");

			var appTitle;

			if(appWords.length>=3)
				appTitle = appWords[0] + " " + appWords[1] + " " + appWords[2];
			else 
				appTitle = appWords.join(appWords);
			

			AppsSummaryInfo_plots[appIds[i]] = {"appName" : appTitle, "Feature_Evals": count_Evals, "Feature_Requests":count_Requests, "Bug_Reports":count_bugs, "sum_sentiment_score_eval": sum_eval_sentiment_score};

			appTitles[appIds[i]] = appTitle;
			appIcons[appIds[i]] = SummaryInfo[appIds[i]]['appIcon'];
			all_apps_review_sents = all_apps_review_sents.concat(ReviewSentsInfo);
		}		

		FeatureSelectedCompleted = true;		

		//console.log(lst_SAFE_extracted_features_eval);
		
		lst_SAFE_extracted_features_eval = [...new Set(lst_SAFE_extracted_features_eval)];
		lst_SAFE_extracted_features_bug = [...new Set(lst_SAFE_extracted_features_bug)];
		lst_SAFE_extracted_features_request = [...new Set(lst_SAFE_extracted_features_request)];

		List_AppFeatures_Description = [...new Set(List_AppFeatures_Description)];
	
		all_review_data_loaded=true;
	}

	if(app_feature_source=="reviews") {
		//console.log("reviews");
		lst_extracted_features_eval = lst_SAFE_extracted_features_eval;
		lst_extracted_features_bug = lst_SAFE_extracted_features_bug;
		lst_extracted_features_request = lst_SAFE_extracted_features_request;
	}
	else if(app_feature_source=="description")
	{
		//console.log("description");
		lst_extracted_features_eval = List_AppFeatures_Description;
		lst_extracted_features_bug = List_AppFeatures_Description;
		lst_extracted_features_request = lst_SAFE_extracted_features_request;
	}

	if(selected_sentCatgory=="E")
		List_AppFeatures = lst_extracted_features_eval;
	else if(selected_sentCatgory=="B")
		List_AppFeatures = lst_extracted_features_bug;
	else if(selected_sentCatgory=="R")
		List_AppFeatures = lst_extracted_features_request;

	SetAppFeaturesTermsForReviewFilter(List_AppFeatures);

	var newobj_AppsSummmaryInfo = JSON.parse(JSON.stringify(AppsSummaryInfo_plots));

	//console.log('SAFE extracted features');
	//console.log(lst_SAFE_extracted_features);

	// object to store the summary informatoion for feature based sentiment information

	//console.log("Bugs ->" + lst_extracted_features_bug.length.toString());

	for(var l=0;l<lst_extracted_features_eval.length;l++)
	{
			appFeature = lst_extracted_features_eval[l];
			featureEvaluationSentCount[appFeature]=0;
	}

	for(var m=0;m<lst_extracted_features_bug.length;m++)
	{
			appFeature = lst_extracted_features_bug[m];
			featureBugsSentCount[appFeature]=0;
	}

	for(var n=0;n<lst_extracted_features_request.length;n++)
	{
			appFeature = lst_extracted_features_request[n];
			featureRequestsSentCount[appFeature]=0;
	}

	// FeatureWiseAppSummarInfo_eval={};
	// FeatureWiseAppSummarInfo_bugs={};
	// FeatureWiseAppSummarInfo_requests={};

	for(var appid in newobj_AppsSummmaryInfo)
	{
		newobj_AppsSummmaryInfo[appid]['Feature_Evals'] = 0;
		newobj_AppsSummmaryInfo[appid]['Feature_Requests'] = 0;
		newobj_AppsSummmaryInfo[appid]['Bug_Reports'] = 0;
		newobj_AppsSummmaryInfo[appid]['sum_sentiment_score_eval'] = 0;

		for(var i=0;i<lst_extracted_features_eval.length;i++)
		{
			appFeature = lst_extracted_features_eval[i];
			FeatureWiseAppSummarInfo_eval[appid + "#" + appFeature] = {'sum_sentiment_score':0, 'frequency':0};
			//FeatureWiseAppSummarInfo_bugs[appid + "#" + appFeature] = {'frequency':0};
		}

		for(var j=0;j<lst_extracted_features_bug.length;j++)
		{
			appFeature = lst_extracted_features_bug[j];
			FeatureWiseAppSummarInfo_bugs[appid + "#" + appFeature] = {'frequency':0};
		}

		for(var k=0;k<lst_extracted_features_request.length;k++)
		{
			appFeature = lst_extracted_features_request[k];
			FeatureWiseAppSummarInfo_requests[appid + "#" + appFeature] = {'frequency':0};
		}
	}

	//console.log(Object.keys(FeatureWiseAppSummarInfo_bugs).length);


	var sent_with_features=0;

	if(all_review_data_searched==false) 
	{
		for(var i=0;i<all_apps_review_sents.length;i++) {
			var review_info = all_apps_review_sents[i];
			var sentCategory = review_info['category'];
			var sentiment_score = review_info['sentiment'];
			var reviewSentWords = review_info['sent_words'];
			var reviewSentWords_stemmed = review_info['sent_stemmed_words'];
			
			var appID = review_info['appID'];

			// in case of feature request , this will be used
			var extracted_featureTerms = review_info['feature_terms'];
		
			var featureTerms_selected= feature_terms_for_filteration.length!=0;

			var match_found=0;
			
			if(featureTerms_selected) {

				var lst_feature_positions=[];

				if(sentCategory=='E' || sentCategory=="B" && app_feature_source=="description")
					lst_feature_positions = GetFeatureWordsIndex(reviewSentWords_stemmed,feature_terms_for_filteration);
				else if (sentCategory=='E' || sentCategory=="B" && app_feature_source=="reviews")
					lst_feature_positions = GetFeatureWordsIndex(reviewSentWords_stemmed,extracted_featureTerms);
				else if (sentCategory=="R" && extracted_featureTerms.length!=0)
					lst_feature_positions = GetFeatureWordsIndex(reviewSentWords_stemmed,extracted_featureTerms);

				var match_count=0, feature_found=[];

				for(var k=0;k<reviewSentWords.length;k++)
				{
					var found= false;

					for(var j=0;j<lst_feature_positions.length;j++)
					{
						var feature_pos = lst_feature_positions[j];

						var wordDistThreshold = Math.abs(parseInt(feature_pos["end"]) - parseInt(feature_pos["start"]));

						if(wordDistThreshold>4)
							break;

						if (k>=feature_pos['start'] && k<=feature_pos['end'])
						{							
							found = true;
							match_count = match_count + 1;

							if(feature_found.indexOf(feature_pos["AppFeature"])==-1)
								feature_found.push(feature_pos["AppFeature"]);
						}
					}
				}

				if(feature_found.length>0 && FeatureSelectedCompleted==true)
				{
					for(var m=0;m<feature_found.length;m++)
					{
						var app_feature = feature_found[m];

						if(sentCategory == "E") {
							var oldFreq = parseInt(FeatureWiseAppSummarInfo_eval[appID + "#" + app_feature]['frequency']);
							var oldSentiment_score = parseInt(FeatureWiseAppSummarInfo_eval[appID + "#" + app_feature]['sum_sentiment_score']);
							FeatureWiseAppSummarInfo_eval[appID + "#" + app_feature]['frequency'] = oldFreq + 1;
							FeatureWiseAppSummarInfo_eval[appID + "#" + app_feature]['sum_sentiment_score'] = oldSentiment_score + parseInt(sentiment_score);
							featureEvaluationSentCount[app_feature] = featureEvaluationSentCount[app_feature] + 1;
						}
						else if (sentCategory == "B")
						{
							//console.log(parseInt(FeatureWiseAppSummarInfo_bugs[appID + "#" + app_feature]['frequency']));
							var key = appID + "#" + app_feature;

							//console.log(key);
							//console.log(FeatureWiseAppSummarInfo_bugs.hasOwnProperty(key));
							if(FeatureWiseAppSummarInfo_bugs.hasOwnProperty(key)) {
								var oldFreq = parseInt(FeatureWiseAppSummarInfo_bugs[appID + "#" + app_feature]['frequency']);
								FeatureWiseAppSummarInfo_bugs[appID + "#" + app_feature]['frequency'] = oldFreq + 1;
								featureBugsSentCount[app_feature] = featureBugsSentCount[app_feature] + 1;
							}
						}
						else if (sentCategory == "R")
						{
							var oldFreq = parseInt(FeatureWiseAppSummarInfo_requests[appID + "#" + app_feature]['frequency']);
							FeatureWiseAppSummarInfo_requests[appID + "#" + app_feature]['frequency'] = oldFreq + 1;
							featureRequestsSentCount[app_feature] = featureRequestsSentCount[app_feature] + 1;
						}
					}

					// Need to ajdust in case of feature requests
					//
					all_apps_review_sents[i]['feature_terms'] = feature_found;
				}

				// update plot summary information

				if (sentCategory == "E" && match_count>0) {
					newobj_AppsSummmaryInfo[appID]['Feature_Evals'] = newobj_AppsSummmaryInfo[appID]['Feature_Evals'] + 1;
					newobj_AppsSummmaryInfo[appID]['sum_sentiment_score_eval'] = newobj_AppsSummmaryInfo[appID]['sum_sentiment_score_eval'] + parseInt(sentiment_score);	
					sent_with_features = sent_with_features  + 1	
				}
				else if (sentCategory == "R" && match_count>0) {
					newobj_AppsSummmaryInfo[appID]['Feature_Requests'] = newobj_AppsSummmaryInfo[appID]['Feature_Requests'] + 1;
					sent_with_features = sent_with_features  + 1;
				}
				else if (sentCategory == "B" && match_count>0)
				{
					newobj_AppsSummmaryInfo[appID]['Bug_Reports'] = newobj_AppsSummmaryInfo[appID]['Bug_Reports'] + 1 ;
					sent_with_features = sent_with_features  + 1;
				}
				
			}
		}
					
		if (feature_terms_for_filteration.length!=0 && sent_with_features>0)
		{
			AppsSummaryInfo_plots = newobj_AppsSummmaryInfo;
		}

		if(data_loaded==true) {
			data_loaded = false;
			//showFrequencySlider();	
			FeatureSelectedCompleted = false;
		}

		all_review_data_searched = true;

		var cntr_featureTerms = document.getElementById('containerAppFeatureTerms');
		cntr_featureTerms.style.display = 'block';

		ShowAppFeature_Checkboxes_Sorted();
		DisplaySummaryChart();
	}
	
}


function showFrequencySlider()
{
	// var slider = document.getElementById("frequency_range");
	// var output = document.getElementById("frequency_value");
	// output.innerHTML = slider.value;
	var selectedReviewmode= getUrlVars()["mode"];
	var feature_extraction_approach = document.getElementById("lstExtractionApproach").value;

	if(selectedReviewmode=="offline")
		if(feature_extraction_approach=="ONE_WORD_NOUN")
			setSliderValue(50);
		else if(feature_extraction_approach=="SAFE")
			setSliderValue(10);
	else if(selectedReviewmode=="live")
		setSliderValue(1);
}

function filterbyAppFeatureTerms() {
 	ShowReviewSummary(ReviewSummaryData);
}

function updateSummaryInfo()
{	
	var selected_sentCatgory = getSelectedSentenceType();
	var selected_frequency = parseInt($("#frequency_range" ).val());
	var app_feature_source=$('input[name=AppFeature_Source]:checked').val();

	//document.getElementById('summaryHeading').innerHTML = "";
	//document.getElementById('summaryHeading').style.display = "none";

	//document.getElementById("review_summary").innerHTML = "";
	//document.getElementById("review_summary").style.display = "none";

	featureTermsSentCount = {};

	if(selected_sentCatgory=="E" || selected_sentCatgory=="B")
	{
		feature_terms_for_filteration = List_AppFeatures;
		feature_terms_for_filteration.sort();
	}
	else if(selected_sentCatgory=="R")
	{
		feature_terms_for_filteration = lst_SAFE_extracted_features_request;
		feature_terms_for_filteration.sort();
	}


	// if(FeatureSelectedCompleted==true) {

		// for(var appid in ReviewSummaryData)
		// {
		// 	for(var j=0;j<feature_terms_for_filteration.length;j++)
		// 	{
		// 		appFeature = feature_terms_for_filteration[j];
		// 		FeatureWiseAppSummarInfo_eval[appid + "#" + appFeature] = {'sum_sentiment_score':0, 'frequency':0};
		// 		FeatureWiseAppSummarInfo_bugs[appid + "#" + appFeature] = {'frequency':0};
		// 		// FeatureWiseAppSummarInfo_requests[appid + "#" + appFeature] = {'frequency':0};
		// 		featureTermsSentCount[appFeature] = 0;
		// 	}
		// }

		// for(var i=0;i<all_apps_review_sents.length;i++) {
		// 	var review_info = all_apps_review_sents[i];
		// 	var sentCategory = review_info['category'];
		// 	var sentiment_score = review_info['sentiment'];
		// 	var featureTerms = review_info['feature_terms'];			

		// 	var appID = review_info['appID'];
			
		// 	if(selected_sentCatgory==sentCategory && featureTerms.length>0) {
		// 		for(var m=0;m<featureTerms.length;m++)
		// 		{
		// 			var app_feature = featureTerms[m];

		// 			featureTermsSentCount[app_feature] = featureTermsSentCount[app_feature] + 1;

		// 			if(sentCategory == "E") {
		// 				var oldFreq = parseInt(FeatureWiseAppSummarInfo_eval[appID + "#" + app_feature]['frequency']);
		// 				var oldSentiment_score = parseInt(FeatureWiseAppSummarInfo_eval[appID + "#" + app_feature]['sum_sentiment_score']);
		// 				FeatureWiseAppSummarInfo_eval[appID + "#" + app_feature]['frequency'] = oldFreq + 1;
		// 				FeatureWiseAppSummarInfo_eval[appID + "#" + app_feature]['sum_sentiment_score'] = oldSentiment_score + parseInt(sentiment_score);
		// 			}
		// 			else if (sentCategory == "B")
		// 			{
		// 				var oldFreq = parseInt(FeatureWiseAppSummarInfo_bugs[appID + "#" + app_feature]['frequency']);
		// 				FeatureWiseAppSummarInfo_bugs[appID + "#" + app_feature]['frequency'] = oldFreq + 1;
		// 			}
		// 		}
		// 	}
		// }
	//}

	ShowAppFeature_Checkboxes_Sorted();

	DisplaySummaryChart();
	
}

function ShowSentencesWithSpecificsentiment(sentiment){
	var sentType_wise_reviewSents = "";
	
	if(sent_count>0)
		sentType_wise_reviewSents = lst_review_sents;

	document.getElementById("review_summary").innerHTML = sentType_wise_reviewSents;
}

function ShowReviewSentencesAgainstSelectedAppFeature_App(appid,app_feature,selected_sentCategory,selected_sentiment=-100)
{

	clicked_appFeature= app_feature;
	clicked_appID = appid;

	var sentimentWiseCounts={'-2':0,'-1':0,'0':0,'1': 0, '2':0};

	document.getElementById("review_summary").style.display = "block";

	if(selected_sentCategory!='E')
		document.getElementById("eval_pieChart").style.display = "none";
	else
		document.getElementById("eval_pieChart").style.display = "block";

	document.getElementById("review_summary").innerHTML = "";

	if(sentSortOrder=="asc")
	{
		sorted_review_sents= all_apps_review_sents.sort(sort_by('sentiment', true, parseInt));
	}
	else if(sentSortOrder=="desc")
	{
	   sorted_review_sents= all_apps_review_sents.sort(sort_by('sentiment', false, parseInt));
	}

	
	var lst_review_sents="";
	var sent_count=0,eval_count=0,bugs_count=0,requests_count=0;


	for(var i=0;i<sorted_review_sents.length;i++) {
		var review_info = sorted_review_sents[i];
		var sentCategory = review_info['category'];
		var sentiment_score = review_info['sentiment'];
		var reviewSentWords = review_info['sent_words'];
		var reviewSentWords_stemmed = review_info['sent_stemmed_words'];
		
		var appID = review_info['appID'];
		var review_sent_id = review_info['sent_id'];
		var featureTerms = review_info['feature_terms'];

		var appIconUrl = ReviewSummaryData[appID]['appIcon'];
		var appName = ReviewSummaryData[appID]['appTitle'];

		// Retrieve review text against sentnece id
		var review_id = review_sent_id.split('#')[0];
		var ReviewsInfo = ReviewSummaryData[appID]['Reviews'];
	
		var txt_review = ReviewsInfo[review_id]['text'];
		txt_review = txt_review.replace(/'/g,"");

		var review_sent_html="";

		var sentTypeIcon="";
		var sentType = "";
		var basePath="src/assets/images/";

		if(sentCategory=="E")
		{
			txt_color = dict_colors[sentiment_score.toString()];
		}
		else if (sentCategory=="B") {
			txt_color = 'Red';
		} else if (sentCategory=="R") {
			txt_color = 'RebeccaPurple';
		} 


		var feature_clicked= featureTerms.indexOf(app_feature.trim())!=-1;

		if (feature_clicked==true) {

			var lst_feature_positions = GetFeatureWordsIndex(reviewSentWords_stemmed,[app_feature.trim()]);

			var review_sent_html="";
			
			var match_count=0;

			for(var k=0;k<reviewSentWords.length;k++)
			{
				var found= false;

				for(var j=0;j<lst_feature_positions.length;j++)
				{
					var feature_pos = lst_feature_positions[j];

					var wordDistThreshold = Math.abs(parseInt(feature_pos["end"]) - parseInt(feature_pos["start"]));

					if(wordDistThreshold>4)
						break;

					if (k>=feature_pos['start'] && k<=feature_pos['end'])
					{
						review_sent_html += "<span style='font-weight:bold;background-color:yellow;'>" + reviewSentWords[k] +"</span>";
						review_sent_html += "<span style='font-weight:bold;background-color:yellow'>" + " "  + "</span>";
						found = true;
						match_count = match_count + 1;
					}
				}

				if(found==false)
				{
					review_sent_html += reviewSentWords[k];
					if(k<reviewSentWords.length-1)
						review_sent_html += " ";
				}

			}

			if(sentCategory=='E' && match_count>0 && appid == appID && selected_sentiment==-100)
			{
				sentimentWiseCounts[sentiment_score.toString()] = sentimentWiseCounts[sentiment_score.toString()] + 1;
			}
			else if (sentCategory=='E' && match_count>0 && appid == appID && selected_sentiment!=-100 && sentiment_score==selected_sentiment) 
			{
				lst_review_sents += "<div id='sentContainer' style='float:left;width:1150px;margin-left:12px;'>";
				lst_review_sents += "<div style='float:left;'>";						
				lst_review_sents += "<span style='float:left;margin-right:10px;font-size:13px;color:" + txt_color + "' '>+<span>";						
				lst_review_sents += "<span style='margin-left:5px;font-size:13px;text-align:justify;text-justify: inter-word;color:" + txt_color + "' title='" + txt_review.trim() + "'>" + review_sent_html.trim() + "</span>";
				//lst_review_sents += "</div>";
				lst_review_sents += "</div></div>";
				lst_review_sents += "<div id='clear'></div>";
				sent_count =  sent_count + 1;
			}
			else if(sentCategory==selected_sentCategory && sentCategory!='E' && match_count>0 && appid == appID){
				//txt_color = dict_colors[sentiment_score.toString()];
				lst_review_sents += "<div id='sentContainer' style='float:left;width:1150px;margin-left:12px;'>";
				lst_review_sents += "<div style='float:left;'>";						
				lst_review_sents += "<span style='float:left;font-size:13px;color:" + txt_color + "' '>+<span>";						
				lst_review_sents += "<span style='font-size:13px;text-align:justify;text-justify: inter-word;color:" + txt_color + "' title='" + txt_review.trim() + "'>" + review_sent_html.trim() + "</span>";
				//lst_review_sents += "</div>";
				lst_review_sents += "</div></div>";
				lst_review_sents += "<div id='clear'></div>";
				sent_count =  sent_count + 1;
			}
		}

	}

	if(selected_sentCategory=='E' && selected_sentiment==-100) {
		var chartData=[];

		for(var key in sentimentWiseCounts)
		{
			var pieColor = dict_colors[key];
			chartData.push({'sentiment_label': dict_sentimentLabels[key], 'count': sentimentWiseCounts[key], 'color': pieColor.toString()});
		}

		console.log(chartData);

		var chart = AmCharts.makeChart( "eval_pieChart", {
			"type": "pie",
			"theme": "none",
			"dataProvider": chartData,
			"valueField": "count",
			"titleField": "sentiment_label",
			"colorField" : "color",
			// "titles": [ {"text":"Distribution of sentiment score in review sentences for app feature '" + app_feature + "'","size":13}],
			"startDuration": 0.0,
			"balloon":{
			"fixedPosition":true
			},
			"listeners": [{
				"event": "clickSlice",
				"method": function(event) {
					var dp = event.dataItem.dataContext;

					//alert(chart.titleField.toString() + "," + dp[chart.titleField].toString());
					var sentiment_label = dp[chart.titleField];

					var sentiment_value= -100;

					if(sentiment_label.trim()=="very negative")
						sentiment_value= -2;
					else if(sentiment_label.trim()=="negative")
						sentiment_value= -1;
					else if(sentiment_label.trim()=="neutral")
						sentiment_value=0;
					else if(sentiment_label.trim()=="positive")
						sentiment_value= 1;
					else if(sentiment_label.trim()=="very positive")
						sentiment_value= 2;

					ShowReviewSentencesAgainstSelectedAppFeature_App(appid,app_feature,selected_sentCategory,sentiment_value);
				}
			  }]
		} );
	}
	else
	{

		// $("#reviews_modalBody").css("height", 500);

		if(selected_sentCategory=='E' && selected_sentiment!=-100)
		{
			var Wintitle = document.getElementById('reviews_winTitle');
			new_msg = popup_msg +  " (" + dict_sentimentLabels[selected_sentiment.toString()] + ")";
			Wintitle.innerHTML = new_msg;
		}

		var sentType_wise_reviewSents = "";
	
		if(sent_count>0)
			sentType_wise_reviewSents = lst_review_sents;
	
		document.getElementById("review_summary").innerHTML = sentType_wise_reviewSents;
	}
}

function ClearTermSearch()
{
	searchTerm = "A";
	$("#slider-range").slider('values',0,0);
	$("#slider-range").slider('values',1,4);
	$('#filterbySentType').val("A");
	$('#filterbyApp').val("A");
 	ShowReviewSummary(ReviewSummaryData);
}

function PopulateAppsList() {
	//var apps = getUrlVars()["ids"].split(',');

	var ctrl= document.getElementById("filterbyApp"); 

	//for (var i =0 ; i< apps.length; i++) {
	for(var appid in appTitles)
	{
		//var opt= apps [i];
		var el = document.createElement("option");
		var appWords = appTitles[appid].split(" ");

		var appTitle;

		if(appWords.length>=2)
			appTitle = appWords[0] + " " + appWords[1];
		else if(appWords.length==1)
			appTitle = appWords[0];

		el.text = appTitle;
		el.value = appid;
		ctrl.appendChild(el);
	}
}

function extractCategories(responseText) {
    this.categories = JSON.parse(responseText);
	drawCategories(this.categories);   
}

//* Applications methods *//
function loadApplications() {
	buttonLoading();
	httpGetAsync(API_URL + "apps?category=" + getUrlVars().categoryId, extractApplications );
}

function applicationsSearchChange() {
	drawApplications(applications, document.getElementById('srch-term').value);
}

function extractApplications(responseText) {
	this.applications = JSON.parse(responseText);
	drawApplications(this.applications);
}

function drawApplications(applications, filter) {
	var container = document.getElementById("check-container");
	var nextButton = document.getElementById("next-button");
	var searchContainer = document.getElementById("search-container");

	$("#next-button").click(function() { applicationsNextClick(); });
	buttonReset();

	clearElements(container, 'radio-div');

    for (var k in applications) {
		if (filter !== undefined && applications[k].title.toLowerCase().indexOf(filter.toLowerCase()) < 0) {
			continue;
		}

		var input = document.createElement("input");
	    input.type = "checkbox";
	    input.id = applications[k].id;
	    input.name = applications[k].title;
	    addOnClick(input, uncheck = false);
	    if (Object.keys(checkedApplicationsCheckboxes).indexOf(input.id) != -1) {
	    	input.checked = true;
	    }

	    var label = document.createElement('label');
	    label.setAttribute("for", input);
	    label.innerHTML = applications[k].title;
	
		var div = document.createElement('div');
		div.setAttribute('class','radio');
		div.setAttribute('id','radio-div');

		div.appendChild(input);
		div.appendChild(label);
		container.appendChild(div);	
    } 

    container.appendChild(nextButton);
}

function NextClick() {
	var selectedReviewmode= "offline"; //document.querySelector('input[name="mode"]:checked').value;
	var main_app = document.getElementById('main_apps').value;
	console.log(main_app);
	if(selectedReviewmode=="live")
	{
		var NumReviews = document.getElementById("txtNumReviews");

		checkedmainApplication.push(main_app);
		var allApps = checkedmainApplication.concat(Object.keys(checkedApplicationsCheckboxes));

		if(txtNumReviews.value!="")
		{
			NumOfReviews = parseInt(txtNumReviews.value);

			if (Object.keys(checkedApplicationsCheckboxes).length === 0) {
				alert("Please choose at least two applications");
			} 
			else 
			{ 
				location_url = 'reviews_summary.html?ids=' + allApps;
				location_url += '&' + 'reviews=' + NumOfReviews + "&" + "mode=live";
				window.location = location_url;
			}
		}
		else
		{
			alert('Please enter the number of reviews!')
		}
	}
	else if (selectedReviewmode=="offline")
	{
		// if(selectedAppsOffline.length<2)
		// 	alert("Please choose at least two applications");
		// else
		// {
		alert('offline mode');
		checkedmainApplication.push(main_app);

		var selectedAppsOffline = checkedmainApplication.concat(Object.keys(checkedApplicationsCheckboxes));
		console.log(selectedAppsOffline); 
		location_url = 'reviews_summary.html?ids=' + selectedAppsOffline;
		location_url += '&' + 'mode=offline';
		window.location = location_url;
		//}
	}
}

function round(num) {
  num = Math.round(num+'e'+2)
  return Number(num+'e-'+2)
}

function createBoldLabel(text, textColor, fontSize) {
	var div = document.createElement('div');
    var label = document.createElement('label');
    label.innerHTML = capitalizeFirstLetter(text);
    label.style.fontWeight = 'bold';

    if (textColor !== undefined) { label.style.color = textColor; }
    if (fontSize !== undefined) { label.style.fontSize = fontSize; }
    
    div.appendChild(label);
    return div;
}

function capitalizeFirstLetter(string) {
	if (string === undefined) { return; }
    return string.charAt(0).toUpperCase() + string.slice(1);
}

// function handleReviewMode(review_mode)
// {
// 	var current_value=review_mode.value;

// 	if(current_value=="live")
// 	{
// 		document.getElementById('lst_offline_apps').style.display = "none";
// 		document.getElementById('page-title').style.display = "block";
// 		document.getElementById('radio-container').style.display = "block";
// 		document.getElementById('next-button').disabled = true;
		
// 	}	
// 	else if(current_value=="offline")
// 	{
// 		document.getElementById('lst_offline_apps').style.display = "block";
// 		document.getElementById('page-title').style.display = "none";
// 		document.getElementById('radio-container').style.display = "none";
// 		document.getElementById('next-button').disabled = false;
// 	}
// }

function loadOfflineApps()
{

	var nextButton = document.getElementById("next-button");

	nextButton.disabled = false;


	loadSimilarApps();

	// var offline_apps=[
	// 			//	{"id":'292760731',"appName": 'Menstrual Calendar FMC',"icon":'https://is2-ssl.mzstatic.com/image/thumb/Purple115/v4/bc/04/56/bc0456a8-4ad6-4f6f-47c4-588499e12403/source/512x512bb.jpg', 'NoOfReviews':'2800'},
	// 			//	{"id":'386022579',"appName": 'Pregnancy Tracker - BabyCenter',"icon":'https://is5-ssl.mzstatic.com/image/thumb/Purple114/v4/bf/2d/d4/bf2dd4e4-3d5d-a098-d443-947cee0f0561/source/512x512bb.jpg', 'NoOfReviews':'5880'},
	// 			//	{"id":'287529757',"appName": 'Calorie Counter - MyNetDiary',"icon":'https://is4-ssl.mzstatic.com/image/thumb/Purple124/v4/40/1e/ca/401eca3a-f97a-2b53-7575-68864888937c/source/512x512bb.jpg', 'NoOfReviews':'6149'},
	// 			//	{"id":'368868193',"appName": 'Period Tracker: Monthly Cycles',"icon":'https://is4-ssl.mzstatic.com/image/thumb/Purple128/v4/08/1f/54/081f54b3-7413-899a-cc32-3e3f5c747d42/source/512x512bb.jpg', 'NoOfReviews':'3004'},
	// 			//	{"id":'436762566',"appName": 'Period Diary',"icon":'https://is2-ssl.mzstatic.com/image/thumb/Purple127/v4/16/13/b5/1613b53d-9f64-591d-6fd8-4aaf84854720/source/512x512bb.jpg', 'NoOfReviews':'10121'},
	// 				{"id":'292987597',"appName": 'White Noise Lite',"icon":'https://is4-ssl.mzstatic.com/image/thumb/Purple118/v4/ac/4c/45/ac4c45ac-4383-1a9f-002e-d43b69b32ff0/source/512x512bb.jpg', 'NoOfReviews':'4939'},
	// 				{"id":'410606661',"appName": 'White Noise Sleep Pillow Sound',"icon":'https://is2-ssl.mzstatic.com/image/thumb/Purple122/v4/6f/91/c7/6f91c751-84ee-6f1f-194f-a8f20794eb20/source/512x512bb.jpg', 'NoOfReviews':'3238'},
	// 			//	{"id":'301521403',"appName": 'Nike Training Club',"icon":'https://is2-ssl.mzstatic.com/image/thumb/Purple128/v4/bb/5f/04/bb5f0481-4833-4ac3-2630-559763eea765/source/512x512bb.jpg', 'NoOfReviews':'3483'},
	// 				{"id":'426826309',"appName": 'Strava: Run, Ride, Swim',"icon":'https://is1-ssl.mzstatic.com/image/thumb/Purple124/v4/6a/bc/e9/6abce96f-97e4-8f9a-f4cc-b4bf4198acec/source/512x512bb.jpg', 'NoOfReviews':'3183'},
	// 				{"id":'298903147',"appName": 'Map My Fitness by Under Armour',"icon":'https://is5-ssl.mzstatic.com/image/thumb/Purple124/v4/90/9a/d7/909ad78a-2227-6571-1224-2805e61c4ff3/source/512x512bb.jpg', 'NoOfReviews':'2709'},
	// 				// {"id":'363724891',"appName": '50,000 Baby Names',"icon":'https://is2-ssl.mzstatic.com/image/thumb/Purple20/v4/4d/88/89/4d8889fd-ac0d-acee-c5aa-10af26d640e7/source/512x512bb.jpg', 'NoOfReviews':'2944'},
	// 				{"id":'398436747',"appName": 'Fooducate Nutrition Tracker',"icon":'https://is1-ssl.mzstatic.com/image/thumb/Purple124/v4/ad/d3/7b/add37b26-7f4d-6e51-c0b6-bf8674b44d61/source/512x512bb.jpg', 'NoOfReviews':'4230'},
	// 				{"id":'509253726',"appName": 'Fitocracy - Fitness Collective',"icon":'https://is2-ssl.mzstatic.com/image/thumb/Purple128/v4/ca/87/08/ca8708d0-70f4-132c-2459-7b8474f2de69/source/512x512bb.jpg', 'NoOfReviews':'2490'},
	// 			//	{"id":'329504506',"appName": 'iHoroscope - Daily Horoscope',"icon":'https://is4-ssl.mzstatic.com/image/thumb/Purple114/v4/f7/3a/61/f73a6107-2d1f-5991-a6d4-dc4a30adfa3b/source/512x512bb.jpg', 'NoOfReviews':'3690'},
	// 				{"id":'292223170',"appName": 'Map My Ride by Under Armour',"icon":'https://is5-ssl.mzstatic.com/image/thumb/Purple124/v4/4a/a4/13/4aa413bf-8df1-44b1-470f-77f62b18c5fc/source/512x512bb.jpg', 'NoOfReviews':'6407'},
	// 				{"id":'300235330',"appName": 'Runkeeper—GPS Running Tracker',"icon":'https://is2-ssl.mzstatic.com/image/thumb/Purple114/v4/0b/67/45/0b674518-fcf5-d309-7821-7e93ca034384/source/512x512bb.jpg', 'NoOfReviews':'3394'},
	// 			//	{"id":'353938652',"appName": 'Baby Names',"icon":'https://is5-ssl.mzstatic.com/image/thumb/Purple128/v4/62/3a/b8/623ab8ae-91a8-c171-569a-2ddb4c0f40e6/source/512x512bb.jpg', 'NoOfReviews':'6189'},
	// 				{"id":'387771637',"appName": 'Nike Run Club',"icon":'https://is3-ssl.mzstatic.com/image/thumb/Purple118/v4/e2/41/ce/e241ce25-4bd2-9242-a9ff-31adb0273d63/source/512x512bb.jpg', 'NoOfReviews':'5764'},
	// 				{"id":'675033630',"appName": 'Taxify',"icon":'https://is2-ssl.mzstatic.com/image/thumb/Purple124/v4/f4/1b/d0/f41bd07c-577f-5e5a-14d2-2d363832ee1a/source/512x512bb.jpg', 'NoOfReviews':'500'},
	// 				{"id":'368677368',"appName": 'Uber',"icon":'https://is5-ssl.mzstatic.com/image/thumb/Purple124/v4/03/97/45/03974578-2604-85a9-96ea-7e8b3b208c67/source/512x512bb.jpg', 'NoOfReviews':'500'},
	// 				{"id":'1291898086',"appName": 'Toggl: Time Tracker for Work',"icon":'https://is1-ssl.mzstatic.com/image/thumb/Purple114/v4/62/f2/66/62f26696-f514-f263-29a5-e7817ff6fbf4/source/512x512bb.jpg', 'NoOfReviews':'500'},
	// 				{"id":'895933956',"appName": 'Hours Time Tracking',"icon":'https://is4-ssl.mzstatic.com/image/thumb/Purple118/v4/e5/b1/33/e5b13342-7220-da45-fc5e-01fb189161cb/source/512x512bb.jpg', 'NoOfReviews':'500'},
	// 				{"id":'336456412',"appName": 'HoursTracker: Hours and Pay',"icon":'https://is1-ssl.mzstatic.com/image/thumb/Purple118/v4/5d/0e/aa/5d0eaade-a762-4edb-c5e9-3dbf6ee1e361/source/512x512bb.jpg', 'NoOfReviews':'500'}
	// ];

	// var div_offline_apps=document.getElementById('lst_offline_apps');
	// var initialTxt="<span style='font-size:14px;'>Select app(s) from the following list of apps:<span><br>";
	// //initialTxt += "<div style='text-align:center;width:800px;'>";
	// initialTxt+= "<div style='height:10px;'></div>";
	// initialTxt+= "<div style='width:20px;float:left;'></div>";
	// initialTxt+= "<div style='width:10px;float:left;margin-left:40px;'></div>";
	// initialTxt+= "<div style='width:250px;float:left;;margin-left:100px;font-weight:bold;'>App Name</div>";
	// initialTxt+= "<div style='width:100px;float:left;margin-left:4px;font-weight:bold;'>No of Reviews</div>";
	// initialTxt+= "<div style='clear:left'></div>";

	// for(var i=0;i<offline_apps.length;i++)
	// {
	// 	var appInfo = offline_apps[i];
	// 	initialTxt +="<div style='width:20px;float:left;'><input type='checkbox' onclick='appSelected(this)' id='" + appInfo['id'] + "' value='" + appInfo['id'] + "' /> </div>";
	// 	initialTxt += "<div style='width:30px;float:left;margin-left:15px;'><img src='" + appInfo['icon'] + "' style='width:20px;height:20px;'/></div>";
	// 	initialTxt += "<div style='width:250px;float:left;margin-left:0px;font-weight:normal'>";
	// 	initialTxt += "<span id='lbl_" + appInfo['id'] + "' style='font-weight:normal;padding-left:0px;'>" + appInfo['appName'] +  "</span></div>";	
	// 	initialTxt += "<div style='width:100px;float:left;margin-left:60px;'><span id='lbl_reviews_" + appInfo['id'] + "' style='font-weight:normal;'>" + appInfo['NoOfReviews'] +  "</span></div>";	
	// 	initialTxt+= "<div style='clear:left;margin-top:20px;'></div>";
	// }

	// div_offline_apps.innerHTML = initialTxt;
}

function appSelected(element)
{
	//unchecking the checked checkbox
	if (element.checked != true) {
		var index = selectedAppsOffline.indexOf(element.value);
		if (index > -1) {
			selectedAppsOffline.splice(index, 1);
		}
		element.checked = false; 
		return;
	}

	selectedAppsOffline.push(element.value);
	element.checked = true;
}

