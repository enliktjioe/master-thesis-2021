//var feature_id=1;

var loaded_description=false;
var CotentMaxHeight;
var active_collapsible_app;
var X_Position;
var Y_Position;
var feature_terms_for_filteration=[];
var curentScreen="";
var featureTermsSentCount={};
var FeatureSelectedCompleted = false;
var chart_visiblity=false;


function AuthenticateUser(userid,pwd)
{
	var api_location = API_URL + "authenticate";
	api_location += "?uid=" + userid + "&pwd=" + pwd;
	httpGetAsync(api_location, getUserAuthenticate);
}

function getUserAuthenticate(responseText)
{
	var result = JSON.parse(responseText);
	if(result["authenticate"]=="true")
	{
		
		sessionStorage.setItem('status','loggedIn') ;
		apps_page_url =  "ShowApps.html";
	//query string data
		apps_page_url += "?uid=" + result['userid'];
	// call rest API
		window.location = apps_page_url;
	}
	else if(result["authenticate"]=="false")
	{
		var errMsg = document.getElementById("ErrorMessage")
		errMsg.innerText = "Wrong username or password. Try again!!";
	}

}

function SortappFeatures(feature1, feature2) {
    var feature1_words = feature1.split(" ");
    var feature2_words =feature2.split(" ");
    
	if (feature1_words.length > feature2_words.length) return -1;
	if (feature1_words.length < feature2_words.length) return 1;

}

function getStemmedFeatures(lst_selectedFeatures) {
	var api_location = API_URL + "stem_features";
	api_location += "?appFeatures=" + JSON.stringify(lst_selectedFeatures);
	httpGetAsync(api_location, show_stemmed_features);
};

function show_stemmed_features(responseText) {
	this.Stemmed_appFeatures = JSON.parse(responseText);
	//console.log(this.Stemmed_appFeatures);
	showStemmdAppFeatures(this.Stemmed_appFeatures['appFeatures']);
}

function showStemmdAppFeatures(appFeatures)
{
	var divModalbody = document.getElementById('modalBody');
	divModalbody.style.display = "block";
	var txtDivBody = "<div class='featureList'>";
	var all_paras_text ="";

	txtDivBody += "<p style='font-size:14px'> <i> Following " + appFeatures.length.toString() + " (unique and stemmed) features are selected: </i> <p>";

	for(var i=0;i<appFeatures.length;i++)
	{
		var app_feature = appFeatures[i];
		all_paras_text += "<span class='feature-wrap-v1'>" +  app_feature + "</span>";

		if (i<appFeatures.length-1)
			{
				all_paras_text += "<span>" + "," + "</span>";
			}
	}

	txtDivBody += all_paras_text;
	txtDivBody += "</div>";
	divModalbody.innerHTML = txtDivBody;
}

function SetAppFeaturesTermsForReviewFilter(lst_appFeatures)
{
	for(var i=0;i<lst_appFeatures.length;i++)
	{
		app_feature = lst_appFeatures[i];
		featureTermsSentCount[app_feature] = 0;
		feature_terms_for_filteration.push(app_feature);
	}

	feature_terms_for_filteration.sort();
	
}

function CountNonZeroFeatureRequestTerms()
{
	var count=0;

	var selected_frequency = parseInt($("#frequency_range").val());

	for(var i=0;i<lst_SAFE_extracted_features_request.length;i++)
	{
		var app_feature = lst_SAFE_extracted_features_request[i];
		var freq = featureRequestsSentCount[app_feature];

		if(freq>=selected_frequency){
			count+=1;
		}
	}

	return count;

}

function CountNonZeroFeatureTerms()
{
	var count=0;

	var selected_frequency = parseInt($("#frequency_range").val());

	for(var i=0;i<feature_terms_for_filteration.length;i++)
	{
		var app_feature = feature_terms_for_filteration[i];
		var freq = featureTermsSentCount[app_feature];

		if(freq>=selected_frequency){
			count+=1;
		}
	}

	return count;

}

function GetFeatureFrequencyStatusOverallApps(sentType,appFeature,frequency_threshold)
{
	var feature_status=true;
	var feature_frequency=0;

	for(var appid in appTitles) {
		var appTitle = appTitles[appid];
		
		if(sentType=="E")
			feature_frequency += parseInt(FeatureWiseAppSummarInfo_eval[appid + "#" + appFeature]['frequency']);
		else if(sentType=="B") {
			var key  = appid + "#" + appFeature;
			if(FeatureWiseAppSummarInfo_bugs.hasOwnProperty(key))
				feature_frequency += parseInt(FeatureWiseAppSummarInfo_bugs[appid + "#" + appFeature]['frequency']);
		}
		else if (sentType=="R")
			feature_frequency += parseInt(FeatureWiseAppSummarInfo_requests[appid + "#" + appFeature]['frequency']);	
	}

	if(feature_frequency<frequency_threshold)
	{
		feature_status= false;
	}

	return {"status":feature_status,"frequency" : feature_frequency};

}

function GetFeatureFrequencyStatusforEachApp(sentType,appFeature,frequency_threshold)
{
	var feature_status=true;
	var overall_frequency=0;

	for(var appid in appTitles) {
		var appTitle = appTitles[appid];
		var feature_frequency=0;

		if(sentType=="E") {
			feature_frequency = parseInt(FeatureWiseAppSummarInfo_eval[appid + "#" + appFeature]['frequency']);
			overall_frequency += parseInt(FeatureWiseAppSummarInfo_eval[appid + "#" + appFeature]['frequency']);
		}
		else if(sentType=="B") {
			feature_frequency = parseInt(FeatureWiseAppSummarInfo_bugs[appid + "#" + appFeature]['frequency']);
			overall_frequency += parseInt(FeatureWiseAppSummarInfo_bugs[appid + "#" + appFeature]['frequency']);
		}
		else if (sentType=="R"){
			feature_frequency = parseInt(FeatureWiseAppSummarInfo_requests[appid + "#" + appFeature]['frequency']);
			overall_frequency += parseInt(FeatureWiseAppSummarInfo_requests[appid + "#" + appFeature]['frequency']);
		}

		if(feature_frequency<frequency_threshold)
		{
			feature_status= false;
			break;
		}
	
	}
	
	return {"status":feature_status,"frequency" : overall_frequency};
}

function FilterModeChanged(elem){
	updateSummaryInfo();
}

function FeatureSourceChanged(elem)
{
	// source to extract app features have changed
	feature_terms_for_filteration=[];
	
	lst_extracted_features_eval=[];
	lst_extracted_features_bug=[];
	lst_extracted_features_request=[];

	FeatureWiseAppSummarInfo_eval={};
	FeatureWiseAppSummarInfo_bugs={};
	FeatureWiseAppSummarInfo_requests={};

	// for (var prop in FeatureWiseAppSummarInfo_bugs) {
	// 	if (FeatureWiseAppSummarInfo_bugs.hasOwnProperty(prop)) {
	// 		delete FeatureWiseAppSummarInfo_bugs[prop];
	// 	}
	// }

	featureRequestsSentCount={};
	featureEvaluationSentCount={};
	featureBugsSentCount={};

	FeatureSelectedCompleted = true;
	all_review_data_searched = false;

	filterbyAppFeatureTerms();

	FeatureSelectedCompleted = false;
}

function ShowAppFeature_Checkboxes_Sorted()
{
	var divFilterByFeatureTerms = document.getElementById('FilterbyFeatureTerms');
	var initialTxt="<input type='checkbox' onclick='checkAll(this)' name='chk[]' value='all' checked/>"
	initialTxt += "<label id='lbl_all'> all</label> <br/>";

	var count=0;

	var selected_frequency = parseInt($("#frequency_range").val());
	var frequency_filter_mode=$('input[name=frequency_mode]:checked').val();
	var sentCategory = document.getElementById("filterbySentType").value;

	feature_terms_for_filteration.sort();

	for(var i=0;i<feature_terms_for_filteration.length;i++)
	{
		var app_feature = feature_terms_for_filteration[i];
		
		if(frequency_filter_mode == "overall")
		{
			//var freq = featureTermsSentCount[app_feature];
			var dict_freq_status_overall_apps = GetFeatureFrequencyStatusOverallApps(sentCategory,app_feature,selected_frequency);
			if(dict_freq_status_overall_apps["status"]==true){
				initialTxt +="<input type='checkbox' onclick='AppFeatureValueChanged(this)' id='" + app_feature + "' value='" + app_feature + "' checked/>";
				initialTxt += "<label id='lbl_" + app_feature + "'>" + app_feature + " (" + dict_freq_status_overall_apps["frequency"].toString() + ")" + "</label>";	
				count+=1;
			}
		}
		else if(frequency_filter_mode == "indiviual")
		{
			var dict_freq_status_indiviual_app = GetFeatureFrequencyStatusforEachApp(sentCategory,app_feature,selected_frequency);

			if(dict_freq_status_indiviual_app["status"]==true){

				initialTxt +="<input type='checkbox' onclick='AppFeatureValueChanged(this)' id='" + app_feature + "' value='" + app_feature + "' checked/>";
				initialTxt += "<label id='lbl_" + app_feature + "'>" + app_feature + " (" + dict_freq_status_indiviual_app["frequency"].toString() + ")" + "</label>";	

				count+=1;
			}
		}
	}
	

	if(count==0)
	{
		divFilterByFeatureTerms.innerHTML = "<span style='text-algin:center; font-style: italic;margin-left:200px;'>No review sentences found. Change app feature frequency filter/mode or modify the list of app feature terms!</span>"
		containerPlots_sentTypes.style.display = "none";
	}
	else
	{
		containerPlots_sentTypes.style.display = "block";
		divFilterByFeatureTerms.innerHTML = initialTxt;
	}

}

function AppFeatureValueChanged(ele)
{
	CheckAllorNot();
	ReadAppFeaturesTermsForReviewFilter();
	//filterbyAppFeatureTerms();
	//ShowChart();
	DisplaySummaryChart();
	//ShowFeatureEvaluationSummaryChart();
}

function CheckAllorNot()
{
	var checkboxes = document.getElementsByTagName('input');

	var checkAll = true;

	if (checkboxes!= undefined)
	{
	
		for (var i = 0; i < checkboxes.length; i++) {
			
			if (checkboxes[i].type == 'checkbox' && checkboxes[i].checked == false && checkboxes[i].value!="all") 
			{
				checkAll = false;
				break;
			}
			
			if (checkboxes[i].type == 'checkbox' && checkboxes[i].value=="all")
			{
				ele = checkboxes[i];
			}
		}

		
		if(checkAll==false && ele.checked)
			ele.checked = false;
		else if(checkAll==true && ele.checked==false)
			ele.checked = true;
		else if(checkAll==true && ele.checked==true)
			ele.checked = true;
	
}


}

function ReadAppFeaturesTermsForReviewFilter()
{
	var checkboxes = document.getElementsByTagName('input');

	feature_terms_for_filteration=[];
	
	for (var i = 0; i < checkboxes.length; i++) {
		if (checkboxes[i].type == 'checkbox' && checkboxes[i].checked && checkboxes[i].value!="all") {
			feature_terms_for_filteration.push(checkboxes[i].value);
		}
	}

	feature_terms_for_filteration.sort(SortappFeatures);
	
}


function checkAll(ele) {
	var checkboxes = document.getElementsByTagName('input');
	if (ele.checked) {
		for (var i = 0; i < checkboxes.length; i++) {
			if (checkboxes[i].type == 'checkbox') {
				checkboxes[i].checked = true;
			}
		}
		
		ReadAppFeaturesTermsForReviewFilter();
		//filterbyAppFeatureTerms();
		//ShowFeatureEvaluationSummaryChart();
		DisplaySummaryChart();
		//filter review senetences based on this selection
	} else {
		for (var i = 0; i < checkboxes.length; i++) {
			if (checkboxes[i].type == 'checkbox') {
				checkboxes[i].checked = false;
			}
		}

		ReadAppFeaturesTermsForReviewFilter();
		//filterbyAppFeatureTerms();
		//ShowFeatureEvaluationSummaryChart();
		DisplaySummaryChart();
		//ShowFeatureEvaluationSummaryChart();
	}

}

function Show_FeatureReview_Window(appID,appFeature,sentCategory)
{
	var modal = document.getElementById('myModal_reviewSummary');
	document.getElementById('reviews_modalBody').style.display="block";

	modal.style.display = "block";	
	var appIconUrl = appIcons[appID]

	var sentType="";

	if(sentCategory=="E")
		sentType = "Feature evaluation";
	else if(sentCategory=="B")
		sentType = "Bug report";
	else if(sentCategory=="R")
		sentType = "Feature request";


	//var msg= "<img src='" + appIconUrl.toString() + "' class='appIcon' title='" + appTitles[appID] + "'>" +"</img>"
	var msg="";

	msg+= "<span>" + sentType + " review sentences" +  " mentioning app feature <u>'" + appFeature + "'</u></span>";

	var Wintitle = document.getElementById('reviews_winTitle');
	Wintitle.innerHTML = msg;

	popup_msg = msg;

	ShowReviewSentencesAgainstSelectedAppFeature_App(appID,appFeature,sentCategory);
}

function ShowAppWiseSentTypeDist()
{
	var modal = document.getElementById('myModal_sentTypePlot');
	modal.style.display = "block";

	document.getElementById('sentTypePlot_modalBody').style.display="block";

	ShowChart();
}

// When the user clicks the button, open the modal 
function OpenFilterWindow() {	

	//showDescription();

	var sentCategory = document.getElementById("filterbySentType").value;
	var app_feature_source=$('input[name=AppFeature_Source]:checked').val();

	if(sentCategory!='R' && app_feature_source!='reviews') {
		var modal = document.getElementById('myModal');
		modal.style.display = "block";	

		document.getElementById("div_set_feature_terms").style.display = "block";
		document.getElementById("divNext").style.display = "none";
		document.getElementById("div_featureExtractionApproach").style.display = "none";
		document.getElementById("modalBody").style.display = "none";
		document.getElementById("div_Manual_AppFeatureTerms").style.display = "none";
		document.getElementById("divback").style.display = "none";
		
		var Wintitle = document.getElementById('winTitle');
		Wintitle.innerHTML = "Choose betweeen manual vs. automatic approach";
		//Wintitle.innerHTML = "Select features terms from app description:";

		curentScreen = "ManualvsSemiAutotomaticApproach";
		document.getElementById("appFeatureshead").click();

	}
	else
	{
		alert('This functionality is only valid for sentenence types: feature evaluation and bug report')
		document.getElementById("appFeatureshead").click();
	}
}

// When the user clicks on <span> (x), close the modal
function CloseFilterWindow() {
	var modal = document.getElementById('myModal');
	// Get the <span> element that closes the modal
	//var span = document.getElementsByClassName("close")[0];
	modal.style.display = "none";	
}

function ClosesentTypePlotWindow()
{
	var modal = document.getElementById('myModal_sentTypePlot');
	// Get the <span> element that closes the modal
	//var span = document.getElementsByClassName("close")[0];
	modal.style.display = "none";	
}

function CloseReviewsWindow()
{
	var modal = document.getElementById('myModal_reviewSummary');
	// Get the <span> element that closes the modal
	//var span = document.getElementsByClassName("close")[0];
	modal.style.display = "none";	
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
	var modal = document.getElementById('myModal');
	var review_modal = document.getElementById('myModal_reviewSummary');
	if (event.target == modal) {
		modal.style.display = "none";
	}

	else if (event.target == review_modal) {
			review_modal.style.display = "none";
	}

}

function changeExtractionApproach() {
	var extractionApproach = document.getElementById("lstExtractionApproach").value;
	showDescription();
}

function removeFeature_NonConsec(event,featureid)
{
	var feature_id_element = document.getElementById(featureid);
	X_Position = event.clientX;
	Y_Position = event.clientY;
	
	featureId_parts = featureid.split("#");
	var appID = featureId_parts[0];
	var sentid = parseInt(featureId_parts[1]);
	var feature_term_index = parseInt(featureId_parts[2]);

	var appDescSents = ReviewSummaryData[appID]["Description"];
	var extractionApproach = document.getElementById("lstExtractionApproach").value;
	
	for(var i=0;i<appDescSents.length;i++) 
	{
		if(i==sentid)
		{
			var non_cont_feature_terms = appDescSents[i]['feature_extraction_results'][extractionApproach]['NON_CONSECUTIVE_TERMS'];

			if (feature_term_index!=-1)
			{
				non_cont_feature_terms.splice(feature_term_index, 1);
				ReviewSummaryData[appID]["Description"][i]['feature_extraction_results'][extractionApproach]['NON_CONSECUTIVE_TERMS'] = non_cont_feature_terms;

				// show the updated contents
				showDescription();
			}


		}
	}
}

function removeFeature(event,featureid)
{
	var feature_id_element = document.getElementById(featureid);
	//feature_id_element.className ="feature-wrap-clear";
	X_Position = event.clientX;
	Y_Position = event.clientY;

	//console.log(X_Position.toString() + "," + Y_Position.toString());
	
	featureId_parts = featureid.split("#");
	var appID = featureId_parts[0];
	var sentid = parseInt(featureId_parts[1]);
	var feature_pos = featureId_parts[2].split('_');
	var start_pos = parseInt(feature_pos[0]);
	var end_pos = parseInt(feature_pos[1]);

	var appDescSents = ReviewSummaryData[appID]["Description"];
	var extractionApproach = document.getElementById("lstExtractionApproach").value;
	
	for(var i=0;i<appDescSents.length;i++) 
	{
		if(i==sentid)
		{
			var sentTokens  = appDescSents[i]['sent_words'];
			var feature_term_positions = appDescSents[i]['feature_extraction_results'][extractionApproach]['CONSECUTIVE_TERMS'];

			var startIndex, endIndex;
			var feature_term_index=-1;

			for(var j=0;j<feature_term_positions.length;j++)
			{	
				startIndex = parseInt(feature_term_positions[j]['start']);
				endIndex = parseInt(feature_term_positions[j]['end']);

				if (startIndex==start_pos && end_pos == endIndex)
				{
					feature_term_index = j;
					break;
				}
			}

			if (feature_term_index!=-1)
			{
				feature_term_positions.splice(feature_term_index, 1);
				ReviewSummaryData[appID]["Description"][i]['feature_extraction_results'][extractionApproach]['CONSECUTIVE_TERMS'] = feature_term_positions;

				// show the updated contents
				showDescription();
			}


		}
	}

}

function getSelectedText() {
	if (window.getSelection) {
		return window.getSelection().toString();
	} else if (document.selection) {
		return document.selection.createRange().text;
	}
	return '';
}

function editFeatures(event,sentID)
{
	var Mainpara = document.getElementById(sentID);
	var btnEdit = document.getElementById(sentID + '_btnEdit');

	X_Position = event.clientX;
	Y_Position = event.clientY;
	
	if (btnEdit.textContent == "Edit" || btnEdit.textContent=="Add") 
	{
		var lstFeatures = document.getElementById(sentID + '_non_consec_features');
		lstFeatures.innerHTML = GetHTML_for_FeaturEditing(sentID);
		btnEdit.textContent = "Save";

		var coll = document.getElementsByClassName("collapsible");
		var i;

		for (i = 0; i < coll.length; i++) 
		{
			if(active_collapsible_app==coll[i].innerHTML) {
				coll[i].click();
				coll[i].click();

				// coll[l].nextElementSibling.style.position = "relative";
				// coll[l].nextElementSibling.scrollTop = Y_Position;
				// coll[l].nextElementSibling.scrollLeft = X_Position;
			}
		}
	}
	else if(btnEdit.textContent == "Save")
	{
		update_non_consecutiveFeatures(sentID);
		var lstFeatures = document.getElementById(sentID + '_non_consec_features');
		lstFeatures.innerHTML = GetHTML_nonConsecutiveFeatures(sentID);
		btnEdit.textContent = "Edit";
	}
	
}

function update_non_consecutiveFeatures(mainParaID)
{
	var id_edit_feature_box= mainParaID +  "_" + 'txtEditFeatures';

	var cntrl_textArea = document.getElementById(id_edit_feature_box);

	var updated_non_consec_features = cntrl_textArea.value.split('\n');

	var extractionApproach = document.getElementById("lstExtractionApproach").value;

	var paraIDInfo = mainParaID.split('#');
	var appid = paraIDInfo[0].toString();
	var SelectedsentNo = parseInt(paraIDInfo[1]);

	var appDescSents = ReviewSummaryData[appid]["Description"];

	for(var j=0;j<appDescSents.length;j++) 
	{
		if (j==SelectedsentNo)
		{
			appDescSents[j]['feature_extraction_results'][extractionApproach]['NON_CONSECUTIVE_TERMS'] = updated_non_consec_features;
			break;
		}
	}
}

function GetHTML_for_FeaturEditing(mainParaID)
{
	var paraIDInfo = mainParaID.split('#');
	var appid = paraIDInfo[0].toString();
	var SelectedsentNo = parseInt(paraIDInfo[1]);

	var appDescSents = ReviewSummaryData[appid]["Description"];
	var non_cont_feature_terms=[];

	var extractionApproach = document.getElementById("lstExtractionApproach").value;

	for(var j=0;j<appDescSents.length;j++) 
	{
		if (j==SelectedsentNo)
		{
			non_cont_feature_terms= appDescSents[j]['feature_extraction_results'][extractionApproach]['NON_CONSECUTIVE_TERMS'];
			break;
		}
	}

	lst_features="";

	for(var j=0;j<non_cont_feature_terms.length;j++)
	{
		lst_features += non_cont_feature_terms[j];

		if (j<non_cont_feature_terms.length-1)
			lst_features += "\n";
	}

	var id_edit_feature_box= mainParaID +  "_" + 'txtEditFeatures';

	var txtHTML="<span>";
	txtHTML += "<textarea id='" + id_edit_feature_box +  "' cols='20' rows='4'>" + lst_features + "</textarea>";
	txtHTML += "</span>";


	return txtHTML;
}

function GotoManual()
{
	var nxt_screen = document.getElementById('div_Manual_AppFeatureTerms');
	nxt_screen.style.display = "block";

	var bck_screen = document.getElementById('div_set_feature_terms');
	bck_screen.style.display = "none";

	var Wintitle = document.getElementById('winTitle');
	Wintitle.innerHTML = "Enter list of app feature terms";

	var Btnbck = document.getElementById("divback");
	Btnbck.style.display = "block";

	var Btnnxt = document.getElementById("divNext");
	Btnnxt.style.display = "block";

	//document.getElementById("btnNext").textContent = "Finish";

	curentScreen = "ManualFeatureTerms";
}

function GotoSemiAutomatic()
{
	var nxt_screen_1 = document.getElementById('div_featureExtractionApproach');
	nxt_screen_1.style.display = "block";

	var nxt_screen_2 = document.getElementById('modalBody');
	nxt_screen_2.style.display = "block";

	var bck_screen = document.getElementById('div_set_feature_terms');
	bck_screen.style.display = "none";

	document.getElementById('div_Manual_AppFeatureTerms').style.display="none";

	var Wintitle = document.getElementById('winTitle');
	Wintitle.innerHTML = "Select feature terms from app description";

	var Btnbck = document.getElementById("divback");
	Btnbck.style.display = "block";

	var Btnnxt = document.getElementById("divNext");
	Btnnxt.style.display = "block";

	curentScreen = "SemiAutomaticFeatureTerms";

	showDescription();
}

function GetHTML_nonConsecutiveFeatures(mainParaID)
{
	var paraIDInfo = mainParaID.split('#');
	var appid = paraIDInfo[0].toString();
	var SelectedsentNo = parseInt(paraIDInfo[1]);

	var extractionApproach = document.getElementById("lstExtractionApproach").value;

	var appDescSents = ReviewSummaryData[appid]["Description"];
	var non_cont_feature_terms=[];

	for(var j=0;j<appDescSents.length;j++) 
	{
		if (j==SelectedsentNo)
		{
			non_cont_feature_terms= appDescSents[j]['feature_extraction_results'][extractionApproach]['NON_CONSECUTIVE_TERMS'];
			break;
		}
	}

	var txt_non_cont_features="";

	if (non_cont_feature_terms.length!=0)
	{		
		txt_non_cont_features += "<span>";
		for(var i=0;i<non_cont_feature_terms.length;i++)
		{
			txt_non_cont_features += "<span class='wrap_non_cont_feature'>" + non_cont_feature_terms[i] + "</span>";

			if(i<non_cont_feature_terms.length-1)
				txt_non_cont_features +=",";
		}

		txt_non_cont_features += "</span>"
	}
	else
	{
		txt_non_cont_features += "<span>";
		txt_non_cont_features += "</span>"

	}


	return txt_non_cont_features;
}

function NewFeatureSelected(sentId) {
	var txtselected = getSelectedText();
	var appID = sentId.split("#")[0];
	var sentid = parseInt(sentId.split("#")[1]);

	var extractionApproach = document.getElementById("lstExtractionApproach").value;

	var appDescSents = ReviewSummaryData[appID]["Description"];

	if(txtselected.trim()!="")
	{
		for(var i=0;i<appDescSents.length;i++) 
		{
			if(i==sentid)
			{
				var sentTokens  = appDescSents[i]['sent_words'];
				var feature_term_positions = appDescSents[i]['feature_extraction_results'][extractionApproach]['CONSECUTIVE_TERMS'];
				var featureWords = txtselected.trim().split(' ');
				var startIndex, endIndex;

				if(featureWords.length==1) {
					startIndex = sentTokens.indexOf(featureWords[0].trim());
					endIndex = startIndex;
				}
				else
				{
					startIndex = sentTokens.indexOf(featureWords[0].trim());
					endIndex = sentTokens.indexOf(featureWords[featureWords.length-1].trim());
				}

				var feature_position={'start': startIndex.toString(),'end':endIndex.toString()};
				feature_term_positions.push(feature_position);

				ReviewSummaryData[appID]["Description"][i]['feature_extraction_results'][extractionApproach]['CONSECUTIVE_TERMS'] = feature_term_positions;

				// show the updated contents
				showDescription();

				break;

			}
		}
	}

}

function GotoBackScreen()
{

	if(curentScreen=="ManualFeatureTerms")
	{ 
		var prv_screen = document.getElementById('div_set_feature_terms')
		prv_screen.style.display = "block";
		var current_screen = document.getElementById('div_Manual_AppFeatureTerms')
		current_screen.style.display = "none";
		curentScreen = "ManualvsSemiAutotomaticApproach";
		var Wintitle = document.getElementById('winTitle');
		Wintitle.innerHTML = "Choose betweeen manual vs. automatic approach";
		var Btnbck = document.getElementById("divback");
		Btnbck.style.display = "none";
		document.getElementById("divNext").style.display = "none";
		
	}
	else if (curentScreen=="Manual_Finished")
	{
		var prev_screen = document.getElementById('div_Manual_AppFeatureTerms')
		prev_screen.style.display = "block";
		var btnNext = document.getElementById('btnNext');
		btnNext.textContent = "Next";

		var prv_screen = document.getElementById('div_set_feature_terms')
		prv_screen.style.display = "none";

		var Wintitle = document.getElementById('winTitle');
		Wintitle.innerHTML = "Enter list of app feature terms";

		var prev_screen = document.getElementById('modalBody')
		prev_screen.style.display = "none";

		curentScreen = "ManualFeatureTerms";
	}
	else if (curentScreen == "SemiAutomaticFeatureTerms")
	{
		var prv_screen = document.getElementById('div_set_feature_terms');
		prv_screen.style.display = "block";

		document.getElementById('div_featureExtractionApproach').style.display = "none";
		document.getElementById('modalBody').style.display = "none";

		curentScreen = "ManualvsSemiAutotomaticApproach";

		var Wintitle = document.getElementById('winTitle');
		Wintitle.innerHTML = "Choose betweeen manual vs. automatic approach";
		var Btnbck = document.getElementById("divback");
		Btnbck.style.display = "none";
		document.getElementById("divNext").style.display = "none";
	}
	else if (curentScreen == "SemiAutomaticFeatureTerms_Finished")
	{
		var Wintitle = document.getElementById('winTitle');
		Wintitle.innerHTML = "Select features terms from app description";
		curentScreen = "SemiAutomaticFeatureTerms";
	
		var featureApproach = document.getElementById('div_featureExtractionApproach');
		featureApproach.style.display = "block";

		document.getElementById('modalBody').style.display = "block";
		
	
		var btnNext = document.getElementById('btnNext');
		btnNext.textContent = "Next";

		var Btnbck = document.getElementById("divback");
		Btnbck.style.display = "block";

		var BtnNext = document.getElementById("divNext");
		BtnNext.style.display = "block";

		showDescription();
	}
}

function GotoNextScreen()
{
	var btnNext = document.getElementById('btnNext');
	
	if (btnNext.textContent=="Next" && curentScreen=="SemiAutomaticFeatureTerms") {
		var divBack = document.getElementById('divback');
		divBack.style.display = 'block';

		var featureApproach = document.getElementsByClassName('FeatureExtractionApproach');
		featureApproach[0].style.display = "none";

		curentScreen="SemiAutomaticFeatureTerms_Finished";

		var Wintitle = document.getElementById('winTitle');
		Wintitle.innerHTML = "List of selected app features (unique and stemmed)";

		btnNext.textContent = "Finish";
		showSelectedFeatures();
	}
	else if (btnNext.textContent=="Next" && curentScreen=="ManualFeatureTerms")
	{		
			var divBack = document.getElementById('divback');
			divBack.style.display = 'block';

			curentScreen="Manual_Finished";

			var prev_screen = document.getElementById("div_Manual_AppFeatureTerms");
			prev_screen.style.display ="none";

			var Wintitle = document.getElementById('winTitle');
			Wintitle.innerHTML = "List of app features (unique and stemmed)";

			var ctrltextArea = document.getElementById("manual_lstAppFeatureTerms");
			var feature_terms = ctrltextArea.value.split('\n');
			btnNext.textContent = "Finish";
			getStemmedFeatures(feature_terms);	

	}
	else if (btnNext.textContent=="Finish")
	{
		feature_terms_for_filteration=[];
		featureTermsSentCount = {};

		FeatureSelectedCompleted = true;
		all_review_data_searched = false;

		var divBack = document.getElementById('divback');
		divBack.style.display = 'none';

		var featureApproach = document.getElementsByClassName('FeatureExtractionApproach');
		featureApproach[0].style.display = "none";

		btnNext.textContent = "Next";

		var modal = document.getElementById('myModal');
		modal.style.display = "none";

		//SetAppFeaturesTermsForReviewFilter(this.Stemmed_appFeatures['appFeatures']);

		List_AppFeatures_Description = [...new Set(this.Stemmed_appFeatures['appFeatures'])];

		//List_AppFeatures = this.Stemmed_appFeatures['appFeatures'];

		var cntr_featureTerms = document.getElementById('containerAppFeatureTerms');

		cntr_featureTerms.style.display = 'block';

		filterbyAppFeatureTerms();

		//updateSummaryInfo();

		//ShowAppFeature_Checkboxes_Sorted();

		//ShowFeatureEvaluationSummaryChart();
		//DisplaySummaryChart();

		FeatureSelectedCompleted = false;
  
	}
}




function GetFeatureWordsIndex(sentWords,SelectedFeaturesSortedbyWords)
{
	var lstFeaturesFound=[], appFeaturesFound=[];
	
	//console.log(SelectedFeaturesSortedbyWords);

    for(var i=0;i<SelectedFeaturesSortedbyWords.length;i++)
    {
        appFeature = SelectedFeaturesSortedbyWords[i];
		appFeatuerWords = appFeature.split(" ");

        var featureLength = appFeatuerWords.length;

		var FeatureWordIndexes=[];
		var FeatureWordFound=[];
		
		var feature_word_count=0;

        for(var j=0;j<featureLength;j++)
        {
            var featureWord = appFeatuerWords[j];

            for(var k=0;k<sentWords.length;k++)
            {
                var sentWord = sentWords[k];

				if(featureWord== sentWord && FeatureWordFound.indexOf(sentWord)==-1)
				{
					FeatureWordIndexes.push(k);
					FeatureWordFound.push(sentWord);
					feature_word_count =  feature_word_count + 1;
				}

				if(feature_word_count==featureLength) break;
            }

        }

        if(lstFeaturesFound.length==0 && FeatureWordIndexes.length== featureLength)
        {
			if (featureLength>1)
			{
				lstFeaturesFound.push({"AppFeature": appFeature,"start":FeatureWordIndexes[0],"end":FeatureWordIndexes[FeatureWordIndexes.length-1]});
			}
            else if(featureLength==1) {
				lstFeaturesFound.push({"AppFeature": appFeature,"start":FeatureWordIndexes[0],"end":FeatureWordIndexes[0]});
			}
        }
        else if(lstFeaturesFound.length > 0 && FeatureWordIndexes.length== featureLength){
			var IsoldFeatureSubSet;
			for(var l=0;l<lstFeaturesFound.length;l++)
            {
                var oldFeature = lstFeaturesFound[l];
                var oldFeatureStart = parseInt(oldFeature['start']);
				var oldFeatureEnd = parseInt(oldFeature['end']);
				//var wordDistThreshold = Math.abs(oldFeatureEnd - oldFeatureStart);

				for(var m=0;m<FeatureWordIndexes.length;m++)
				{
					if(FeatureWordIndexes[m]>=oldFeatureStart && FeatureWordIndexes[m]<=oldFeatureEnd)
					{
						IsoldFeatureSubSet = true;
						break;
					}
					else
					{   
						IsoldFeatureSubSet = false;
					}
				}
			}
				
			if(IsoldFeatureSubSet==false && FeatureWordIndexes.length==1)
			{
				lstFeaturesFound.push({"AppFeature": appFeature , "start":FeatureWordIndexes[0],"end":FeatureWordIndexes[0]});
			}
			else if(IsoldFeatureSubSet==false && FeatureWordIndexes.length>1)
			{
				lstFeaturesFound.push({"AppFeature": appFeature , "start":FeatureWordIndexes[0],"end":FeatureWordIndexes[FeatureWordIndexes.length-1]});
			}
			            
        }            
        
    }

    return lstFeaturesFound;
}


function showHide()
{
	if(document.getElementById('FilterbyFeatureTerms').className=="showFeatures") {
		document.getElementById('FilterbyFeatureTerms').className = 'hideFeatures';
		document.getElementById('appFeatureshead').className = 'feature_inactive';
	}
	else if(document.getElementById('FilterbyFeatureTerms').className=="hideFeatures") {
		document.getElementById('FilterbyFeatureTerms').className = 'showFeatures';
		document.getElementById('appFeatureshead').className = 'feature_active';
	}
	
}

function showHidePlots()
{
	if(document.getElementById('SummaryPlots').className=="showPlots") {
		document.getElementById('SummaryPlots').className = 'hidePlots';
		document.getElementById('Plots_head').className = 'SummmaryPlots_inactive';
	}
	else if(document.getElementById('SummaryPlots').className=="hidePlots") {
		document.getElementById('SummaryPlots').className = 'showPlots';
		document.getElementById('Plots_head').className = 'SummmaryPlots_active';
	}
	
}

function showHideSentTypePlots()
{
	if(document.getElementById('SummaryPlot_sentTypes').className=="showSentTypePlots") {
		document.getElementById('SummaryPlot_sentTypes').className = 'hideSentTypePlots';
		document.getElementById('Plots_sentType_head').className = 'SentTypesPlots_inactive';
	}
	else if(document.getElementById('SummaryPlot_sentTypes').className=="hideSentTypePlots") {
		document.getElementById('SummaryPlot_sentTypes').className = 'showSentTypePlots';
		document.getElementById('Plots_sentType_head').className = 'SentTypesPlots_active';
	}
	
}

function DisplaySummaryChart()
{
	var sentType = getSelectedSentenceType();
	
	ReadAppFeaturesTermsForReviewFilter();

	if(feature_terms_for_filteration.length>0)
	{
		if(sentType=='E')
		{		
			document.getElementById('plot_feature_level').style.display = "block";
			ShowFeatureEvaluationSummaryChart();
		}
		else if(sentType=='B')
		{
			document.getElementById('plot_feature_level').style.display = "block";
			ShowBugsSummaryChart();
		}
		else if(sentType=='R')
		{	
			document.getElementById('plot_feature_level').style.display = "block";
			ShowFeatureRequestsSummaryChart();
		}



	}
	else
	{
		document.getElementById('plot_feature_level').style.display = "none";
	}
	
}


function ShowBugsSummaryChart()
{
	var app_frequency_feature_wise={};
	var lst_app_titles=[];

	var selected_frequency = parseInt($("#frequency_range").val());

	const lst_appFeatures = feature_terms_for_filteration.sort();

	var chartData=[];
	var ChartGraph=[];
	var guide_Xlabels=[];
	var guide_Ylabels=[];

	// var nonZeroAppFeatures=[];

	// for(var i=0;i<lst_appFeatures.length;i++)
	// {
	// 		var appFeature = lst_appFeatures[i];

	// 		if(featureTermsSentCount[appFeature]>=selected_frequency) {
	// 			nonZeroAppFeatures.push(appFeature);
	// 		}
	// }

	// nonZeroAppFeatures.sort();


	for(var i=0;i<lst_appFeatures.length;i++)
	{
			var appFeature = lst_appFeatures[i];

			guide_Xlabels.push({"value":i, "label":appFeature,"lineAlpha":0});

			Apps_FeatureData={};

			for(var appid in appTitles) {
				var appTitle = appTitles[appid];

				var feature_frequency = parseInt(FeatureWiseAppSummarInfo_bugs[appid + "#" + appFeature]['frequency']);
			
				Apps_FeatureData[appid + "_feature"]= i;
				Apps_FeatureData[appid + "_frequency"] = feature_frequency;
				Apps_FeatureData[appid + "_bullet"] = appIcons[appid];
				Apps_FeatureData["label"] = appFeature;
				chartData.push(Apps_FeatureData);
		}

	}

	//console.log(chartData);

	//setting up graph

	for(var appid in appTitles) {
		var appTitle = appTitles[appid];
		var x= appid + "_feature";
		var y= appid + "_frequency";
		var image = appid + "_bullet";

		var iconPath = appIcons[appid];

		app_graph_info={"balloonText": "App Feature:<b>[[label]]</b><br>Frequency:<b>[[y]]</b>",
		"valueField": 20,"xField" : x, "yField": y, "bullet" : "custom", "customBulletField" : image, "lineAlpha": 0, "fillAlphas":0, "bulletBorderAlpha":0.2, "minBulletSize":20, "maxBulletSize":30, "customMarker" : iconPath, "markerType" : "none", "title" : appTitles[appid],"id":appid};
		ChartGraph.push(app_graph_info);
	}


	// fill data for chart

	var chart = AmCharts.makeChart("plot_feature_level", {
		"type": "xy",
		"path": "https://www.amcharts.com/lib/3/",
		"theme": "light",
		"titles" : [{"text":"Frequency of app features in review sentence type \'bug report\'"}],
		"legend": {
			"useGraphSettings": true,
			"align" : "center",
			"position" : "top",
			"markerType" : "none",
			"markerSize" : 20,
			"spacing" : 5
		  },
		"dataProvider": chartData,
		"valueAxes": [ {
		  "position": "bottom",
		  "title" : "App feature terms",
		  "axisAlpha": 1,
		  "labelsEnabled": false,
		  "guides" : guide_Xlabels,
		   "minMaxMultiplier": 1.01,
		 "labelRotation": 45
		}, {
		  "axisAlpha": 0,
		  "title" : "Frequency",
		   //"minimum" : 1,
		//   "maximum" : 2.1,
		   "step": 1,
		  "position": "left",
		  "integersOnly" : true,
		   "minMaxMultiplier": 1.01
		} ],
		"startDuration": 0.0,
		"graphs": ChartGraph,
		// "marginLeft" : 46,
		// "marginBottom":35,
		"chartScrollbar":{},
		"chartCursor":{},
		"listeners": [{
			"event": "clickGraphItem",
			"method": function(event) {
			  var appFeature= lst_appFeatures[event.item.dataContext[event.graph.xField]];
			  var frequency= event.item.dataContext[event.graph.yField];
			  var appID = event.graph.id; 
			  if(parseInt(frequency)>0)
				Show_FeatureReview_Window(appID,appFeature,"B");
			  	//ShowReviewSentencesAgainstSelectedAppFeature_App(appID,appFeature,"B");
			}
		  }]
	  } );

	
	
}

function ShowFeatureRequestsSummaryChart()
{
	var app_frequency_feature_wise={};
	var lst_app_titles=[];

	var selected_frequency = parseInt($("#frequency_range").val());

	const lst_appFeatures = feature_terms_for_filteration.sort();

	var chartData=[];
	var ChartGraph=[];
	var guide_Xlabels=[];
	var guide_Ylabels=[];


	for(var i=0;i<lst_appFeatures.length;i++)
	{
			var appFeature = lst_appFeatures[i];

			guide_Xlabels.push({"value":i, "label":appFeature,"lineAlpha":0});

			Apps_FeatureData={};

			for(var appid in appTitles) {
				var appTitle = appTitles[appid];

				var feature_frequency = parseInt(FeatureWiseAppSummarInfo_requests[appid + "#" + appFeature]['frequency']);
			
				Apps_FeatureData[appid + "_feature"]= i;
				Apps_FeatureData[appid + "_frequency"] = feature_frequency;
				Apps_FeatureData[appid + "_bullet"] = appIcons[appid];
				Apps_FeatureData["label"] = appFeature;
				chartData.push(Apps_FeatureData);
		}

	}

	//setting up graph

	for(var appid in appTitles) {
		var appTitle = appTitles[appid];
		var x= appid + "_feature";
		var y= appid + "_frequency";
		var image = appid + "_bullet";

		var iconPath = appIcons[appid];

		app_graph_info={"balloonText": "App Feature:<b>[[label]]</b><br>Frequency:<b>[[y]]</b>",
		"valueField": 20,"xField" : x, "yField": y, "bullet" : "custom", "customBulletField" : image, "lineAlpha": 0, "fillAlphas":0, "bulletBorderAlpha":0.2, "minBulletSize":20, "maxBulletSize":70, "customMarker" : iconPath, "markerType" : "none", "title" : appTitles[appid],"id":appid};
		ChartGraph.push(app_graph_info);
	}


	//console.log(chartData);


	// fill data for chart

	var chart = AmCharts.makeChart("plot_feature_level", {
		"type": "xy",
		"path": "https://www.amcharts.com/lib/3/",
		"theme": "light",
		"titles" : [{"text":"Frequency of app features in review sentence type \'feature request\'"}],
		"legend": {
			"useGraphSettings": true,
			"align" : "center",
			"position" : "top",
			"markerType" : "none",
			"markerSize" : 20,
			"spacing" : 5
		  },
		"dataProvider": chartData,
		"valueAxes": [ {
		  "position": "bottom",
		  "title" : "App feature terms",
		  "axisAlpha": 1,
		  "labelsEnabled": false,
		  //"marginLeft" : 50,
		  "guides" : guide_Xlabels,
		   "minMaxMultiplier": 1.01,
		 "labelRotation": 45
		}, {
		  "axisAlpha": 0,  
		  "title" : "Frequency",
		    // "minimum" : -1,
		    // "maximum" : 9,
		   "step": 1,
		  "position": "left",
		  "integersOnly" : true,
		//   "minMaxMultiplier": 1.05
		} ],
		"startDuration": 0.0,
		"graphs": ChartGraph,
		  //"marginLeft" : 50,
		//  "marginBottom":35,
		"chartScrollbar":{},
		"chartCursor":{},
		"listeners": [{
			"event": "clickGraphItem",
			"method": function(event) {
			  var appFeature= lst_appFeatures[event.item.dataContext[event.graph.xField]];
			  var frequency= event.item.dataContext[event.graph.yField];
			  var appID = event.graph.id; 
			  if(parseInt(frequency)>0)
			  	Show_FeatureReview_Window(appID,appFeature,"R");
			  	//ShowReviewSentencesAgainstSelectedAppFeature_App(appID,appFeature,"R");
			}
		  }]
	  } );
}

function ShowFeatureEvaluationSummaryChart()
{
	
	var app_sentiments_feature_wise={};
	var app_frequency_feature_wise={};
	var lst_app_titles=[];

	var selected_frequency = parseInt($("#frequency_range").val());

	//prepare data for plot
	const lst_appFeatures = feature_terms_for_filteration.sort();

	var chartData=[];
	var ChartGraph=[];
	var guide_Xlabels=[];
	var guide_Ylabels=[];

	// var nonZeroAppFeatures=[];

	// for(var i=0;i<lst_appFeatures.length;i++)
	// {
	// 		var appFeature = lst_appFeatures[i];

	// 		if(featureTermsSentCount[appFeature]>=selected_frequency) {
	// 			nonZeroAppFeatures.push(appFeature);
	// 		}
	// }

	// nonZeroAppFeatures.sort();


	for(var i=0;i<lst_appFeatures.length;i++)
	{
			var appFeature = lst_appFeatures[i];

			console.log(appFeature);

			guide_Xlabels.push({"value":i, "label":appFeature,"lineAlpha":0});

			Apps_FeatureData={};

			for(var appid in appTitles) {
				var appTitle = appTitles[appid];

				var feature_frequency = parseInt(FeatureWiseAppSummarInfo_eval[appid + "#" + appFeature]['frequency']);
				var sum_sentiment_score = parseInt(FeatureWiseAppSummarInfo_eval[appid + "#" + appFeature]['sum_sentiment_score']);

				var feature_avg_sentiment_score=0;

				if(feature_frequency!=0)
					feature_avg_sentiment_score = (sum_sentiment_score/feature_frequency).toFixed(2);
			
				Apps_FeatureData[appid + "_sentiment"]=parseFloat(feature_avg_sentiment_score);
				Apps_FeatureData[appid + "_feature"]= i;
				Apps_FeatureData[appid + "_frequency"] = feature_frequency;
				Apps_FeatureData[appid + "_bullet"] = appIcons[appid];
				Apps_FeatureData["label"] = appFeature;
				chartData.push(Apps_FeatureData);
		}

	}


	//setting up graph

	for(var appid in appTitles) {
		var appTitle = appTitles[appid];
		var x= appid + "_feature";
		var y= appid + "_sentiment";
		var freq = appid + "_frequency";
		var image = appid + "_bullet";

		var iconPath = appIcons[appid];

		app_graph_info={"balloonText": "App Feature:<b>[[label]]</b> <br> Sentiment:<b>[[y]]</b><br>Frequency:<b>[[value]]</b>",
		 "valueField": freq, "xField" : x, "yField": y, "bullet" : "custom", "customBulletField" : image, "lineAlpha": 0, "fillAlphas":0, "bulletBorderAlpha":0.2, "minBulletSize":5, "maxBulletSize":70, "customMarker" : iconPath, "markerType" : "none", "title" : appTitles[appid],"id":appid};
		ChartGraph.push(app_graph_info);
	}

	// fill data for chart

	var chart = AmCharts.makeChart( "plot_feature_level", {
		"type": "xy",
		"path": "https://www.amcharts.com/lib/3/",
		"theme": "light",
		"titles" : [{"text":"Sentiment analysis and frequency of app features in review sentence type \'feature evaluation\'"}],
		"legend": {
			"useGraphSettings": true,
			"align" : "center",
			"position" : "top",
			"markerType" : "none",
			"markerSize" : 25,
			"spacing" : 5
		  },
		"dataProvider": chartData,
		"valueAxes": [ {
		  "position": "bottom",
		  "title" : "App feature terms",
		  "axisAlpha": 1,
		  "labelsEnabled": false,
		  "guides" : guide_Xlabels,
		  "minMaxMultiplier": 1.01,
		 "labelRotation": 45
		}, {
		  "axisAlpha": 0,
		  "title" : "Average sentiment score",
		  "minimum" : -2.1,
		  "maximum" : 2.1,
		  "step": 1,
		  "position": "left",
		  "integersOnly" : true,
		  "minMaxMultiplier": 1.01
		} ],
		"startDuration": 0.0,
		"graphs": ChartGraph,
		// "marginLeft" : 46,
		// "marginBottom":35,
		"chartScrollbar":{},
		"chartCursor":{},
		"listeners": [{
			"event": "clickGraphItem",
			"method": function(event) {
			  var appFeature= lst_appFeatures[event.item.dataContext[event.graph.xField]];
			  var frequency= event.item.dataContext[event.graph.valueField];
			  var appID = event.graph.id; 
			  if(parseInt(frequency)>0)
				  //ShowReviewSentencesAgainstSelectedAppFeature_App(appID,appFeature);
				  Show_FeatureReview_Window(appID,appFeature,"E");
			}
		  }]
	  } );
  	
}

function ShowChart() {
	//var plts = document.getElementById('containerPlots');

	var lst_apps=[];
	var lst_featureEvals=[];
	var lst_featureRequests=[];
	var lst_bugReports=[];
	var lst_avgSentimentScore=[];

	//console.log(AppsSummaryInfo_plots);

	for (app_id in AppsSummaryInfo_plots){

		var appTitle = AppsSummaryInfo_plots[app_id]["appName"];

		lst_apps.push(appTitle);
		lst_featureEvals.push(AppsSummaryInfo_plots[app_id]["Feature_Evals"]);
		lst_featureRequests.push(AppsSummaryInfo_plots[app_id]["Feature_Requests"]);
		lst_bugReports.push(AppsSummaryInfo_plots[app_id]["Bug_Reports"]);

		var sum_eval_sentiment_score = AppsSummaryInfo_plots[app_id]["sum_sentiment_score_eval"]
		var count_Evals = AppsSummaryInfo_plots[app_id]["Feature_Evals"];
		var Eval_avg_sentiment_score=0;

		if(count_Evals!=0)
			Eval_avg_sentiment_score = (sum_eval_sentiment_score/count_Evals).toFixed(2);

		lst_avgSentimentScore.push(Eval_avg_sentiment_score);
	  }

	//$("#plotsentTypeDistribution").remove();
	//$("#plotsentTypeDistribution").append('<canvas id="pltsentTypeDistribution"></canvas>')

	var ctx = document.getElementById('pltsentTypeDistribution').getContext('2d');

	//ctx.destory();

	var myChart = new Chart(ctx, {
		type: 'bar',
		data: {
			labels: lst_apps,
			datasets: [
				{ label : 'feature evaluation', data:lst_featureEvals, backgroundColor: '#fce584'},
				{ label : 'feature request', data:lst_featureRequests, backgroundColor: '#86b0cc'},
				{ label : 'bug report', data:lst_bugReports, backgroundColor: '#960018'}
			]
		},
		options: {
			scales: {
				xAxes: [{stacked: true, labelFontWeight : "bold",
					ticks: {
						autoSkip: false
					}
					}],
				yAxes: [{ stacked: true, display: true,
					scaleLabel: {
						display: true,
						labelString: '# of review sentences'
					} }]
	},
	title: {
		display: true,
		text: 'Distribution of review sentence types'
	}
	}
		
	});

	//myChart.update();

	// bkcolors = lst_avgSentimentScore.map(s => barColor(s));
	// //console.log(bkcolors);

	// $("#pltSentimentSummary").remove();
	// $("#plotSentimentSummary").append('<canvas id="pltSentimentSummary"></canvas>')

	// var ctx_plot2 = document.getElementById('pltSentimentSummary').getContext('2d');
	// var Chart_SentimentSummary = new Chart(ctx_plot2, {
	// 								type: 'bar',
	// 								data: {
	// 								labels: lst_apps,
	// 								datasets: [
	// 									{ label : 'Average sentiment score (Feature Evaluation)', data:lst_avgSentimentScore, backgroundColor: bkcolors},
	// 								]
	// 							 },
	// 							 options: {
	// 								scales: {
	// 									xAxes: [{ ticks: {
	// 											autoSkip: false
	// 										}
	// 										}],
	// 									yAxes: [{
	// 										ticks: {
	// 											max: 4,
    //             								min: 0,
    //             								stepSize: 1
	// 										},
	// 										display: true,
	// 										scaleLabel: {
	// 											display: true,
	// 											labelString: 'Avg. sentiment score'
	// 										}
	// 									}]
	// 							},
	// 							legend: sentimentLabelLegend(),
	// 							title: {
	// 								display: true,
	// 								text: 'Average sentiment score (Sentence type: Feature evaluation)'
	// 							}
	// 						}

	// });

	//Chart_SentimentSummary.update();
}

function sentimentLabelLegend() {
	var theHelp = Chart.helpers;
	var sentValues = {0: "0 - 1.5", 0.99: "1.5 - 2.5", 1.99: "2.5 - 4.0"};

	return {
			display: true,
			labels: {
				generateLabels: function(chart) {
			        var labelArray = [];
			        for (var objIndex in sentValues) {
			        	labelArray.push({
							text: sentValues[objIndex],
							fillStyle: barColor(parseFloat(objIndex) + 1),
							index: objIndex
						});
					}
			        
			        return labelArray;
		      	}	
		    }
		};
}

function barColor(value) {
	var greenColor = '#6aaa96';
	var orangeColor = 'rgb(189,140,195)';
	var redColor = '#f95d6a';

	if (value > 2.5) {
		return greenColor;
	} else if (value >= 1.5) {
		return orangeColor;
	} else {
		return redColor;
	}
}

function showSelectedFeatures()
{
	var all_features=[];

	var selected_apps= getUrlVars()["ids"].split(',');

	var extractionApproach = document.getElementById("lstExtractionApproach").value;

	for(var i=0;i<selected_apps.length;i++) 
	{
		var appid = selected_apps[i];
		var appDescSents = ReviewSummaryData[appid]["Description"];
		var appName  = ReviewSummaryData[appid]["appTitle"];

		for(var j=0;j<appDescSents.length;j++) 
		{
			var sentTokens  = appDescSents[j]['sent_words'];
			var loc_sentFeatures = appDescSents[j]['feature_extraction_results'][extractionApproach]['CONSECUTIVE_TERMS'];
			var lst_NonConsecutive_Features = appDescSents[j]['feature_extraction_results'][extractionApproach]['NON_CONSECUTIVE_TERMS'];
			var start_pos;
			var end_pos;

			for(var pos=0;pos<loc_sentFeatures.length;pos++) 
			{
				start_pos = parseInt(loc_sentFeatures[pos]['start']);
				end_pos = parseInt(loc_sentFeatures[pos]['end']);

				var dist = end_pos - start_pos;

				var app_feature="";

				for(var k=0;k<sentTokens.length;k++)
				{
					if (k>=start_pos && k<=end_pos)
					{
						app_feature += sentTokens[k];

						if (dist>0)
							app_feature += " ";
						
						dist = dist - 1;
					}
				}

				if(app_feature!="")
					all_features.push(app_feature);

			}

			if(lst_NonConsecutive_Features.length!=0)
				all_features = all_features.concat(lst_NonConsecutive_Features);	
		}
		
	}

	getStemmedFeatures(all_features);	
}

function showDescription()
{
	var divModalbody = document.getElementById('modalBody');
	var selected_apps = getUrlVars()["ids"].split(',');

	var extractionApproach = document.getElementById("lstExtractionApproach").value;

	var txtDivBody = "";

	for(var i=0;i<selected_apps.length;i++) 
	{
		var appid = selected_apps[i];
		var appDescSents = ReviewSummaryData[appid]["Description"];
		var appName  = ReviewSummaryData[appid]["appTitle"];

		var collapsible_Heading = "<button class='collapsible'>" + appName + "</button>";		
		var collapsible_contents = "<div class='content'>" ;
		collapsible_contents += "<p class='head_contents_con'>" + "Candidate consecutive app feature"  + "</p>";
		collapsible_contents += "<p class='head_contents_non_con'>" + "Candidate non-consecuitve app features"  + "</p>";

		var all_paras_text="";

		for(var j=0;j<appDescSents.length;j++) 
		{
			var sentTokens  = appDescSents[j]['sent_words'];

			var loc_sentFeatures;
			var non_cont_feature_terms;
			var feature_extraction_approach={};
		
			var feature_extraction_approach = appDescSents[j]['feature_extraction_results'][extractionApproach];
			
			var loc_sentFeatures = feature_extraction_approach['CONSECUTIVE_TERMS'];
			var non_cont_feature_terms = feature_extraction_approach['NON_CONSECUTIVE_TERMS'];

			var sentID= appid.toString() + "#" + j.toString();
			var txt_sent_para="<p id='" + sentID + "' onmouseup=\"NewFeatureSelected('"+ sentID + "')\" class='descSentence'>";
			var feature_found=false;
			var txt_app_feature="";
			var dist=-1;
			var start_pos;
			var end_pos;

			for(var k=0;k<sentTokens.length;k++) 
			{
				var sentWord = sentTokens[k];

				if (dist==-1) 
				{
					for(var pos=0;pos<loc_sentFeatures.length;pos++) 
					{
						start_pos = parseInt(loc_sentFeatures[pos]['start']);
						end_pos = parseInt(loc_sentFeatures[pos]['end']);

						// consecutive or contineous feature terms
						if (k>=start_pos && k<=end_pos) 
						{	
							dist = end_pos - start_pos;

							feature_id = sentID + "#" + start_pos.toString() + "_" + end_pos.toString();

							txt_app_feature = "<span class='feature-wrap' onclick=\"removeFeature(event,'" +  feature_id.toString()  +   "')\" id='" + feature_id.toString() + "'><span class='close'>&times;</span>";
							txt_app_feature +="<span>" + sentWord + "</span>";

							//feature_id = feature_id + 1;
	
							dist = dist - 1;

							feature_found = true;
							break;
						}
						
					}

				}
				else if (dist!=-1)
				{
					if (k < sentTokens.length) 
						txt_app_feature += "<span>" + " " + "</span>";
							
					txt_app_feature += "<span>" + sentWord + "</span>";

					dist = dist - 1;
				}

				if(feature_found==true && dist==-1) 
				{
					txt_app_feature += "</span>";
					txt_sent_para += txt_app_feature;
					txt_app_feature = "";
					feature_found = false;
				}
				else if (dist==-1 && feature_found == false)
				{
					txt_sent_para += "<span>" + sentWord + "</span>";
				}

				if (k < sentTokens.length) 
					txt_sent_para += "<span>" + " " + "</span>";
			}

			txt_sent_para += "</p>";
			var txt_non_cont_features ="";
			//var txt_non_cont_features="<p style='float:left' id='" + sentID + "_non_consec_features_header" + "'>";
			//txt_non_cont_features += "<span class='non_consecutive_terms_head'> App feature terms (non-consecutive) => </span>"; 
			//txt_non_cont_features += "</p>"
			txt_non_cont_features +="<p class='non_cont_features' id='" + sentID + "_non_consec_features" + "'>";

			var btn_text="";
		
			if (non_cont_feature_terms.length!=0)
			{				
				txt_non_cont_features += "<span> ";
				for(var m=0;m<non_cont_feature_terms.length;m++)
				{
					feature_id_non_cont = sentID + "#" + m.toString();
					txt_non_cont_features += "<span class='wrap_non_cont_feature' onclick=\"removeFeature_NonConsec(event,'" +  feature_id_non_cont.toString()  +   "')\" id='" + feature_id_non_cont.toString() + "'>" + "<span class='close'>&times;</span>";
					txt_non_cont_features+= "<span>" + non_cont_feature_terms[m] + "</span>";
					txt_non_cont_features += "</span>"

					if(m<non_cont_feature_terms.length-1)
						txt_non_cont_features +=",";
				}

				//txt_non_cont_features += "]";

				txt_non_cont_features += "</span>";
				
				//txt_sent_para += txt_non_cont_features;

				btn_text="Edit";
			}
			else
			{
				txt_non_cont_features += "<span></span>";
				btn_text="Add";
				//txt_sent_para += txt_non_cont_features;
			}

		
			txt_non_cont_features += "</p>";
			txt_sent_para += txt_non_cont_features;

			txt_sent_para += "<p class='editButton' id='" + sentID + "_" + "paraEdit" + "'>";
			txt_sent_para += "<button onclick=\"editFeatures(event,'" + sentID + "')\" id='" + sentID + "_btnEdit" + "' style='height:20px;width:40px;font-size:12px;'>" + btn_text + "</button>";
			txt_sent_para += "</p>";
			txt_sent_para += "<div style='clear:left;height:0;line-height:0;overflow:hidden;display:block'></div>";

			all_paras_text += txt_sent_para;
		
		}

		all_paras_text += "</div>";

		collapsible_contents += all_paras_text;

		txtDivBody += collapsible_Heading;
		txtDivBody += collapsible_contents;
	}

	divModalbody.innerHTML = txtDivBody;

	var coll = document.getElementsByClassName("collapsible");

	for (var i = 0; i < coll.length; i++) 
	{
		coll[i].addEventListener("click", function() 
		{
			this.classList.toggle("active");
			var content = this.nextElementSibling;

			if (content.style.maxHeight){
				content.style.maxHeight = null;
			} 
			else 
			{
				//content.style.maxHeight = content.scrollHeight + "px";
				content.style.maxHeight =  "350px";
				CotentMaxHeight = content.style.maxHeight;
				active_collapsible_app = this.innerHTML;
			} 
		});
	}

	if (loaded_description==false)
		loaded_description=true;
	else
	{	

		var coll = document.getElementsByClassName("collapsible");
		for (var l = 0; l < coll.length; l++) 
		{	
			var content = this.nextElementSibling;
			if(active_collapsible_app==coll[l].innerHTML) {
				coll[l].classList.toggle("active");
				coll[l].nextElementSibling.style.maxHeight = CotentMaxHeight;

				//coll[l].nextElementSibling.style.position = "relative";
				coll[l].nextElementSibling.scrollTop = Y_Position;
				coll[l].nextElementSibling.scrollLeft = X_Position;
				//coll[l].nextElementSibling.style.scrollTop = Y_Position + 'px';
				//coll[l].nextElementSibling.style.left = X_Position  + 'px';
				//coll[l].nextElementSibling.style.top = Y_Position + 'px';

				//console.log(X_Position.toString() + "," + Y_Position.toString());
				
			}
		}
	}
}


