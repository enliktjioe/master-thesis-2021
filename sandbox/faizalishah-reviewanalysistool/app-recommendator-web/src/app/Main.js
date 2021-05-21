var categories;
var applications;
var seachedApplications;
var API_URL = "http://localhost:8081/";

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
var SelectAppReviewData = {};
//var AppWise_FeatureSummary={};
var offline_apps_loaded = false;

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

var data_loaded=false;getReviewsSummary

function getReviewsSummary() {

	if (sessionStorage.getItem('status') != "loggedIn") {
		login_page_url =  "index.html";
		window.location = login_page_url;
	}

	api_location = API_URL + "review_summary";
	//query string data
	api_location += "?ids=" + getUrlVars()["ids"];
	// call rest API
	data_loaded = true;
	httpGetAsync(api_location, ExtractSummary);	
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
	var url = API_URL + "Top10similarAppsInfo?appId=" + main_app;
	httpGetAsync(url, getSimilarApps);
};

function getSimilarApps(responseText) {
	var similarApplications = JSON.parse(responseText);
	drawSimilarApplications(similarApplications);
}

function drawSimilarApplications(similarApplications)
{

	var similarAppsDiv = document.getElementById("similar-apps-div");
	similarAppsDiv.innerHTML = "";

	var nextButton = document.getElementById("next-button");

	var title = createBoldLabel("You have the option to select app(s) from the following list of competitor apps for comparison:", '#208c22', 15);
	title.style.marginTop = "15px";
	similarAppsDiv.appendChild(title);

	var count=0;
	for(var k=0;k<similarApplications.length;k++) {
		var input = document.createElement("input");
		input.type = "checkbox";
		input.name = similarApplications[k].title;
		input.id = similarApplications[k].Competitor_appID;
		addOnClick(input, uncheck = false,addChosenAppsAboveCategories);
		if (Object.keys(checkedApplicationsCheckboxes).indexOf(input.id) != -1) {
			input.checked = true;
		}
	
		var label = document.createElement('label');
		label.setAttribute("for", input);
		label.innerHTML = similarApplications[k].title + " (" + similarApplications[k].NoOfReviews.toString() + ")";
		label.setAttribute('style','margin-left:2px;font-weight:normal;font-size:13px;');
	
		var div = document.createElement('div');
		div.setAttribute('style','margin-left:10px;float:left;');
		
		div.appendChild(input);
		div.appendChild(label);
		similarAppsDiv.appendChild(div);	
	

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
	//var selectedReviewmode= getUrlVars()["mode"];
	var feature_extraction_approach = document.getElementById("lstExtractionApproach").value;
	var app_feature_source=$('input[name=AppFeature_Source]:checked').val();
	
	//alert(sentCategory);
	var lst_apps = getUrlVars()["ids"].split(',');

	if(lst_apps.indexOf("com.nike.plusgps")!=-1)
	{
		if(sentCategory=="R") {
			setSliderValue(5);
		}
		else if(sentCategory=="E") {
			if(app_feature_source=="description")
				setSliderValue(2);
			else if (app_feature_source=="reviews")
				setSliderValue(15);
		}
		else if(sentCategory=="B") {
			if(app_feature_source=="description")
				setSliderValue(2);
			else if (app_feature_source=="reviews")
				setSliderValue(5);
		}
	}
	else 
	{
		if(sentCategory=="R") {
			setSliderValue(2);
			//document.getElementById('lnkModify').onclick = DisplayMsg();
		}
		else if(sentCategory=="E") {
			if(feature_extraction_approach=="ONE_WORD_NOUN")
				setSliderValue(5);
			else if (feature_extraction_approach=="SAFE")
				setSliderValue(2);
		}
		else if(sentCategory=="B") {
			if(feature_extraction_approach=="ONE_WORD_NOUN")
				setSliderValue(2);
			else if (feature_extraction_approach=="SAFE")
				setSliderValue(2);
		}
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

function GetUniqueFeatures(app_features) { 
	var lstAppFeatures = app_features.filter(a => a !== "");
	var lst_UniqueAppFeatures = Array.from(lstAppFeatures);
	//console.log('before->')
	//console.log(lst_UniqueAppFeatures);
    for(var k=0;k<lstAppFeatures.length;k++) {
    	var feature_words_a = lstAppFeatures[k].split(" ");
        var duplicate_indexes=[];
    	for(var i=0;i<lstAppFeatures.length;i++) {
    		if(i!=k) {
        		var found=0;
        		var feature_words_b = lstAppFeatures[i].split(" ");
       
            	if(feature_words_a.length == feature_words_b.length) {
    				for(var j=0;j<feature_words_a.length;j++) {
                		var feature_word = feature_words_a[j];
                		if(feature_words_b.indexOf(feature_word)!=-1) {
                    		found = found + 1;
                    	}	// end of if
                	} // end of for
                
               		 if(found==feature_words_a.length)
               		 {
                   		 if(lst_UniqueAppFeatures[i]!="") {
								duplicate_indexes.push(i);
								lstAppFeatures[i] = "";
                   		 } 
                	}   // end of if
         
            } // end of if
        
       } // end of if (i!=k)
       
    } // end of inner loop
     
    if(duplicate_indexes.length>0) {
    	for(var l=0;l<duplicate_indexes.length;l++){
        	var itemIndex = duplicate_indexes[l];
        	if(lst_UniqueAppFeatures[itemIndex]!="") {	
    			lst_UniqueAppFeatures[itemIndex] = "";
           } // if
        }  // loop
    }  // if
    
} // end of outer loop

//console.log('after->')
//console.log(lst_UniqueAppFeatures.filter(a => a !== ""));

return lst_UniqueAppFeatures.filter(a => a !== "");

} //main function


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
		
		// lst_SAFE_extracted_features_eval = [...new Set(lst_SAFE_extracted_features_eval)];
		// lst_SAFE_extracted_features_bug = [...new Set(lst_SAFE_extracted_features_bug)];
		// lst_SAFE_extracted_features_request = [...new Set(lst_SAFE_extracted_features_request)];

		lst_SAFE_extracted_features_eval =  GetUniqueFeatures(lst_SAFE_extracted_features_eval);
		lst_SAFE_extracted_features_bug = GetUniqueFeatures(lst_SAFE_extracted_features_bug);
		lst_SAFE_extracted_features_request = GetUniqueFeatures(lst_SAFE_extracted_features_request);


		// List_AppFeatures_Description = [...new Set(List_AppFeatures_Description)];

		List_AppFeatures_Description = GetUniqueFeatures(List_AppFeatures_Description);

		//console.log("Discription->", List_AppFeatures_Description);
	
		all_review_data_loaded=true;
	}

	//console.log(app_feature_source);

	
	

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

	
	//console.log(app_feature_source + "->", List_AppFeatures);

	SetAppFeaturesTermsForReviewFilter(List_AppFeatures);

	//console.log("Feature terms->",feature_terms_for_filteration);

	var newobj_AppsSummmaryInfo = JSON.parse(JSON.stringify(AppsSummaryInfo_plots));

	//console.log(lst_SAFE_extracted_features_eval.length);
	//console.log(lst_SAFE_extracted_features_eval);

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
			var extracted_featureTerms = extracted_featureTerms.filter(a => a !== "");
			//if(sentCategory=='E' && extracted_featureTerms.length!=0)
				//console.log(extracted_featureTerms);
		
			var featureTerms_selected= feature_terms_for_filteration.length!=0;
			

			var match_found=0;
			
			if(featureTerms_selected) {

				var lst_feature_positions=[];

				if ((sentCategory=='E' || sentCategory=="B") && app_feature_source=="reviews") {

					for(var n=0;n<extracted_featureTerms.length;n++)
					{
						var safe_extracted_feature= extracted_featureTerms[n];
						var feature_position = GetFeatureWordsIndex(reviewSentWords_stemmed,[safe_extracted_feature]);

						if(feature_position.length==1)
							lst_feature_positions.push(feature_position[0]);
					}
				}
				else if (sentCategory=="R" && extracted_featureTerms.length!=0) {

					for(var n=0;n<extracted_featureTerms.length;n++)
					{
						var safe_extracted_feature= extracted_featureTerms[n];
						var feature_position = GetFeatureWordsIndex(reviewSentWords_stemmed,[safe_extracted_feature]);

						if(feature_position.length==1)
							lst_feature_positions.push(feature_position[0]);
					}
					
				}
				else if((sentCategory=='E' || sentCategory=="B") && app_feature_source=="description") {
					//lst_feature_positions = GetFeatureWordsIndex(reviewSentWords_stemmed,feature_terms_for_filteration);
					//console.log)
					for(var n=0;n<feature_terms_for_filteration.length;n++)
					{
						var safe_extracted_feature= feature_terms_for_filteration[n];
						//console.log(safe_extracted_feature);
						var feature_position = GetFeatureWordsIndex(reviewSentWords_stemmed,[safe_extracted_feature]);

						if(feature_position.length==1)
							lst_feature_positions.push(feature_position[0]);
					}

				}

				var match_count=0, feature_found=[];

				//if(sentCategory=="E")
					//console.log(extracted_featureTerms,"->",lst_feature_positions,"->",reviewSentWords_stemmed);

				//console.log(reviewSentWords_stemmed);
				//console.log(lst_feature_positions);

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

						var new_app_feature = app_feature;

						//console.log(FeatureWiseAppSummarInfo_eval);

						if(sentCategory == "E") {
							//console.log(app_feature,"=>",reviewSentWords_stemmed);
							//console.log(appID + "#" + app_feature, FeatureWiseAppSummarInfo_eval[appID + "#" + app_feature]['frequency'].toString());

							var key = appID + "#" + app_feature;

							if((key in FeatureWiseAppSummarInfo_eval)==false) {
								var app_feature_words = app_feature.split(" ");
								if(app_feature_words.length==2) 
								{
									key = appID + "#" + app_feature_words[1] + " " + app_feature_words[0];
									new_app_feature = app_feature_words[1] + " " + app_feature_words[0];
								}
							
							}

							if(key in FeatureWiseAppSummarInfo_eval) {

								var oldFreq = parseInt(FeatureWiseAppSummarInfo_eval[key]['frequency']);
								var oldSentiment_score = parseInt(FeatureWiseAppSummarInfo_eval[key]['sum_sentiment_score']);
								FeatureWiseAppSummarInfo_eval[key]['frequency'] = oldFreq + 1;
								FeatureWiseAppSummarInfo_eval[key]['sum_sentiment_score'] = oldSentiment_score + parseInt(sentiment_score);
								featureEvaluationSentCount[new_app_feature] = featureEvaluationSentCount[new_app_feature] + 1;
							}
							
						}
						else if (sentCategory == "B")
						{
							//console.log(parseInt(FeatureWiseAppSummarInfo_bugs[appID + "#" + app_feature]['frequency']));
							var key = appID + "#" + app_feature;

							if((key in FeatureWiseAppSummarInfo_bugs)==false) {
								var app_feature_words = app_feature.split(" ");
								if(app_feature_words.length==2) {
									key = appID + "#" + app_feature_words[1] + " " + app_feature_words[0];
									new_app_feature = app_feature_words[1] + " " + app_feature_words[0];
								}
							}

							//console.log(key);
							//console.log(FeatureWiseAppSummarInfo_bugs.hasOwnProperty(key));
							if(FeatureWiseAppSummarInfo_bugs.hasOwnProperty(key)) {
								var oldFreq = parseInt(FeatureWiseAppSummarInfo_bugs[key]['frequency']);
								FeatureWiseAppSummarInfo_bugs[key]['frequency'] = oldFreq + 1;
								featureBugsSentCount[new_app_feature] = featureBugsSentCount[new_app_feature] + 1;
							}
						}
						else if (sentCategory == "R")
						{
							var key = appID + "#" + app_feature;

							if((key in FeatureWiseAppSummarInfo_requests)==false) {
								var app_feature_words = app_feature.split(" ");
								if(app_feature_words.length==2) {
									key = appID + "#" + app_feature_words[1] + " " + app_feature_words[0];
									new_app_feature = app_feature_words[1] + " " + app_feature_words[0];
								}
							}

							if(key in FeatureWiseAppSummarInfo_requests) {
								var oldFreq = parseInt(FeatureWiseAppSummarInfo_requests[key]['frequency']);
								FeatureWiseAppSummarInfo_requests[key]['frequency'] = oldFreq + 1;
								featureRequestsSentCount[new_app_feature] = featureRequestsSentCount[new_app_feature] + 1;
							}
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
	//var selectedReviewmode= getUrlVars()["mode"];
	var feature_extraction_approach = document.getElementById("lstExtractionApproach").value;

	var lst_apps = getUrlVars()["ids"].split(',');
	var app_feature_source=$('input[name=AppFeature_Source]:checked').val();

	if(lst_apps.indexOf("com.nike.plusgps")!=-1)
	{
		if(app_feature_source=="reviews")
				setSliderValue(15);
		else if (app_feature_source=="description")
				setSliderValue(5);
	}
	else if(feature_extraction_approach=="SAFE")
			setSliderValue(2);
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

	var mainContainer = document.getElementById("divFeatureDetails");
	mainContainer.innerHTML="";

	//var sentimentWiseCounts={'-2':0,'-1':0,'0':0,'1': 0, '2':0};

	// document.getElementById("review_summary").style.display = "block";

	// if(selected_sentCategory!='E')
	// 	document.getElementById("eval_pieChart").style.display = "none";
	// else
	// 	document.getElementById("eval_pieChart").style.display = "block";

	// document.getElementById("review_summary").innerHTML = "";

	if(sentSortOrder=="asc")
	{
		sorted_review_sents= all_apps_review_sents.sort(sort_by('sentiment', true, parseInt));
	}
	else if(sentSortOrder=="desc")
	{
	   sorted_review_sents= all_apps_review_sents.sort(sort_by('sentiment', false, parseInt));
	}
	
	//var lst_review_sents="";
	//var sent_count=0,eval_count=0,bugs_count=0,requests_count=0;

	var AppWise_FeatureSummary={};

	for(var app_id in appTitles)
	{
		AppWise_FeatureSummary[app_id] = {"HTMLreviewSents": '','SentCount':0,'sentimentWiseCounts':{'-2':0,'-1':0,'0':0,'1': 0, '2':0}};
	}


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

			
			if(sentCategory==selected_sentCategory && match_count>0){

				var app_review_sent="";

				app_review_sent += "<div id='sentContainer' style='float:left;width:1150px;margin-left:12px;'>";
				app_review_sent += "<div style='float:left;'>";						
				app_review_sent += "<span style='float:left;font-size:13px;color:" + txt_color + "' '>+<span>";						
				app_review_sent += "<span style='font-size:13px;text-align:justify;text-justify: inter-word;color:" + txt_color + "' title='" + txt_review.trim() + "'>" + review_sent_html.trim() + "</span>";
				//lst_review_sents += "</div>";
				app_review_sent += "</div></div>";
				app_review_sent += "<div id='clear'></div>";

				if (typeof AppWise_FeatureSummary[appID]["HTMLreviewSents"]!="undefined"){
					var AppReviewSents = AppWise_FeatureSummary[appID]["HTMLreviewSents"];
					AppReviewSents = AppReviewSents + app_review_sent;
					AppWise_FeatureSummary[appID]["HTMLreviewSents"] = AppReviewSents;
				}
				else
				{	
					AppWise_FeatureSummary[appID]["HTMLreviewSents"] = app_review_sent;
				}

				if(selected_sentCategory=="E") {
					if (AppWise_FeatureSummary[appID]["sentimentWiseCounts"]!=undefined){
						var sentimentWiseCounts = AppWise_FeatureSummary[appID]["sentimentWiseCounts"];
						sentimentWiseCounts[sentiment_score.toString()] = sentimentWiseCounts[sentiment_score.toString()] + 1;
						AppWise_FeatureSummary[appID]["sentimentWiseCounts"] = sentimentWiseCounts;
					}
				}

				var app_review_count = parseInt(AppWise_FeatureSummary[appID]['SentCount']);
				AppWise_FeatureSummary[appID]['SentCount'] = app_review_count + 1;
			
				//sent_count =  sent_count + 1;
			}
		}

	}


	if(selected_sentCategory=='E') {

		var count=1;

		//console.log(AppWise_FeatureSummary);		

		for(app_id in AppWise_FeatureSummary){

			var chartData=[];

			var html_appReveiws="";
			var appIconUrl = appIcons[app_id];
			var appTitle = appTitles[app_id];

			var sentimentWiseCounts = AppWise_FeatureSummary[app_id]["sentimentWiseCounts"];

			var appIconHTML = "<img src='" + appIconUrl.toString() + "' class='appIcon' title='" + appTitles[app_id] + "'>" +"</img>"
			var head_div= "<div style=\"font-weight:bold;font-size:14px;margin-left:5px;margin-bottom:2px;\">" + appIconHTML + "<span style=\"margin-left:2px;\">" +  appTitle + " </span></div>";
			
			html_appReveiws = head_div;
		
			var lst_app_review_sents = AppWise_FeatureSummary[app_id]["HTMLreviewSents"];

			html_appReveiws += lst_app_review_sents;

			var freq = AppWise_FeatureSummary[app_id]["SentCount"];

			if(freq>0) {

				var appContainer = document.createElement('div');
				appContainer.id = app_id + "_container";
				appContainer.setAttribute("style",'width:100%');

				var cid = 'pieChart_' + count;

				var app_reviewSents = document.createElement('div');
				app_reviewSents.id = app_id + "_" + "reviewSents";
				app_reviewSents.setAttribute("style",'width:65%;float:left;');
				app_reviewSents.innerHTML="";
				app_reviewSents.innerHTML=html_appReveiws;

				var app_pieChart = document.createElement('div');
				app_pieChart.id = cid;
				
				app_pieChart.setAttribute("style", "float:left;width:35%;display:block;height:300px;margin-top:-85px;margin-bottom:-30px;");

				var app_clear = document.createElement('div');
				app_clear.id = app_id + "_" + "clearDiv"; 
				app_clear.setAttribute("style",'clear:left;');

				appContainer.appendChild(app_reviewSents);
				appContainer.appendChild(app_pieChart);
				appContainer.appendChild(app_clear);
				mainContainer.appendChild(appContainer);
				

				for(var key in sentimentWiseCounts)
				{
					var pieColor = dict_colors[key];
					chartData.push({'sentiment_label': dict_sentimentLabels[key], 'count': sentimentWiseCounts[key], 'color': pieColor.toString()});
				}


				var chart = AmCharts.makeChart(cid, {
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
					}
				
				} );
			}

			count = count + 1;
		}

		// var sentType_wise_reviewSents = "";

		// // DISPLAY APP WISE REVIEW SENTENCES

		// var appIconUrl = appIcons[app_id];
		// var appTitle = appTitles[app_id];
		// var freq = AppWise_FeatureSummary[app_id]["SentCount"];
		// var lst_app_review_sents = AppWise_FeatureSummary[app_id]["HTMLreviewSents"];

		// if(freq>0)
		// {
		// 	var appIconHTML = "<img src='" + appIconUrl.toString() + "' class='appIcon' title='" + appTitles[app_id] + "'>" +"</img>"
		// 	var head_div= "<div style=\"font-weight:bold;font-size:12px;\">" + appIconHTML + "<span style=\"margin-left:2px;\">" +  appTitle + " </span></div>";
				
		// 	var html_appReveiws = head_div;
		// 	html_appReveiws += lst_app_review_sents;
		// 	sentType_wise_reviewSents += html_appReveiws;
		// }

	}
	else
	{

		// DISPLAY APP WISE REVIEW SENTENCES

		for(app_id in AppWise_FeatureSummary){

			var appIconUrl = appIcons[app_id];
			var appTitle = appTitles[app_id];
			var freq = AppWise_FeatureSummary[app_id]["SentCount"];
			var lst_app_review_sents = AppWise_FeatureSummary[app_id]["HTMLreviewSents"];

			if(freq>0)
			{
				var html_appReveiws="";

				var appIconHTML = "<img src='" + appIconUrl.toString() + "' class='appIcon' title='" + appTitles[app_id] + "'>" +"</img>"
				var head_div= "<div style=\"font-weight:bold;font-size:12px;\">" + appIconHTML + "<span style=\"margin-left:2px;\">" +  appTitle + " </span></div>";
				
				var html_appReveiws = head_div;
				html_appReveiws += lst_app_review_sents;
				//sentType_wise_reviewSents += html_appReveiws;

				var app_reviewSents = document.createElement('div');
				app_reviewSents.id = app_id + "_" + "reviewSents";
				app_reviewSents.setAttribute("style",'width:100%;float:left;');
				app_reviewSents.innerHTML="";
				app_reviewSents.innerHTML=html_appReveiws;

				mainContainer.appendChild(app_reviewSents);
			}
		}


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
	var main_app = document.getElementById('main_apps').value;
	checkedmainApplication.push(main_app);
	var selectedAppsOffline = checkedmainApplication.concat(Object.keys(checkedApplicationsCheckboxes));
	location_url = 'reviews_summary.html?ids=' + selectedAppsOffline;
	window.location = location_url;
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

function GetBaseApps(responseText)
{
	MainAppsData = JSON.parse(responseText);
	FillOfflinesAppInfo(MainAppsData);
}

function FillOfflinesAppInfo(BaseApps)
{
	var main_app = document.getElementById('main_apps');

	if (offline_apps_loaded==false) {
		for(var i = 0; i < BaseApps.length; i++) {
			var MainAppInfo = BaseApps[i];
			var appName = MainAppInfo.title;
			var option = document.createElement("option");
			option.text = appName  + " (" + MainAppInfo.NoOfReviews + ")";
			option.value = MainAppInfo.appId;
			main_app.add(option);
		}

		loadSimilarApps();
		
		offline_apps_loaded = true;
	}
}

function logout()
{
	sessionStorage.setItem('status',null);
	return true;
}

function loadOfflineApps()
{

	//console.log(sessionStorage.getItem('status'));

	if (sessionStorage.getItem('status') != "loggedIn") {
		login_page_url =  "index.html";
		window.location = login_page_url;
	}

	var nextButton = document.getElementById("next-button");
	nextButton.disabled = false;
	var Main_AppID = document.getElementById('main_apps').value
	api_location = API_URL + "BaseAppsInfo?uid=" + getUrlVars()["uid"];
	
	httpGetAsync(api_location, GetBaseApps);
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

