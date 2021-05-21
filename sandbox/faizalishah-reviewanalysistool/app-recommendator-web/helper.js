var reviewSents =[
//    ["it","is","easy","to","read","and","annotate","files","through","this","app","."],
//    ["it","does","not","allow","to","edit","very","large","files"],
//    ["i","wish","it","allow","me","to","edit","very","simple","pdf","files"],
//    ["i","wish","there","would","be","an","option","to","upload","mp3","videos","."],
//     ["i","was","looking","for","an","option","to","highlight","and","annotate","text","in","pdf","documents"],
    ["i","also","valu","the","abil","to","secur","share","select","file","and","to","download","onto","anoth","devic"]
];

//var selectedFeatures=["read files","pdf documents","highlight text","upload videos","edit files","edit pdf files","upload audio"];
var selectedFeatures=["store file","share folder","powerpoint file","recent file","share file","bring file","see file detail"];

function HighlightFeaturesInAppReviews()
{

    var SelectedFeaturesSortedbyWords= selectedFeatures.sort(SortappFeatures);

    document.write("List of selected app features -> ")

    for(var j=0;j<SelectedFeaturesSortedbyWords.length;j++)
    {
        document.write(SelectedFeaturesSortedbyWords[j])

        if (j<SelectedFeaturesSortedbyWords.length-1)
            document.write(",");
    }

    document.write("<br>");
    document.write("++++++++++++++++++++++++++++++++++++++++<br>")


    var i;

    for(i=0;i<reviewSents.length;i++)
    {
       var sent_words=reviewSents[i];
       var lst_feature_positions = GetFeatureWordsIndex(sent_words,SelectedFeaturesSortedbyWords);

       var review_sent_html="";

       for(var k=0;k<sent_words.length;k++)
       {
           var found= false;

            for(var j=0;j<lst_feature_positions.length;j++)
            {
                var feature_pos = lst_feature_positions[j];

                if (k>=feature_pos['start'] && k<=feature_pos['end'])
                {
                    review_sent_html += "<span style='font-weight:bold;background-color:yellow;'>" + sent_words[k] +"</span>";
                    review_sent_html += "<span style='font-weight:bold;background-color:yellow'>" + " "  + "</span>";
                    found = true;
                }
            }

            if(found==false)
            {
                review_sent_html += sent_words[k];
                if(k<sent_words.length-1)
                    review_sent_html += " ";
            }
           
       }


       document.write(review_sent_html);
       document.write("<br>");
       document.write('--------------------------------------------------------');
       document.write("<br>");
    }
}

function GetFeatureWordsIndex(sentWords,SelectedFeaturesSortedbyWords)
{
    var lstFeaturesFound=[];

    for(var i=0;i<SelectedFeaturesSortedbyWords.length;i++)
    {
        appFeature = SelectedFeaturesSortedbyWords[i];
        appFeatuerWords = appFeature.split(" ");

        var featureLength = appFeatuerWords.length;

        var FeatureWordIndexes=[];

        for(var j=0;j<featureLength;j++)
        {
            var featureWord = appFeatuerWords[j];


            for(var k=0;k<sentWords.length;k++)
            {
                var sentWord = sentWords[k];

                if(featureWord== sentWord)
                    FeatureWordIndexes.push(k);
            }

        }

        if(lstFeaturesFound.length==0 && FeatureWordIndexes.length== featureLength)
        {
            if (featureLength>1)
                lstFeaturesFound.push({"start":FeatureWordIndexes[0],"end":FeatureWordIndexes[FeatureWordIndexes.length-1]});
            else if(featureLength==1)
                lstFeaturesFound.push({"start":FeatureWordIndexes[0],"end":FeatureWordIndexes[0]});
        }
        else if(lstFeaturesFound.length > 0 && FeatureWordIndexes.length== featureLength){
            for(var l=0;l<lstFeaturesFound.length;l++)
            {
                var oldFeature = lstFeaturesFound[l];
                var oldFeatureStart = parseInt(oldFeature['start']);
                var oldFeatureEnd = parseInt(oldFeature['end']);

                var IsoldFeatureSubSet;

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

                if(IsoldFeatureSubSet==false && FeatureWordIndexes.length==1)
                {
                    lstFeaturesFound.push({"start":FeatureWordIndexes[0],"end":FeatureWordIndexes[0]});
                }
                else if(IsoldFeatureSubSet==false && FeatureWordIndexes.length>1)
                {
                    lstFeaturesFound.push({"start":FeatureWordIndexes[0],"end":FeatureWordIndexes[FeatureWordIndexes.length-1]});
                }
                
            }
        }            
        
    }

    return lstFeaturesFound;
}

function SortappFeatures(feature1, feature2) {
    var feature1_words = feature1.split(" ");
    var feature2_words =feature2.split(" ");
    
	if (feature1_words.length > feature2_words.length) return -1;
	if (feature1_words.length < feature2_words.length) return 1;

}