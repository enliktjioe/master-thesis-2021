# app-recommendator-api

## instructions

Navigate to the project direcctory with terminal and execute the commands
1. npm install
2. npm install https://github.com/ashalva/app-store-scraper.git
3. npm start

Then the server will start...

### Methods
#### Retrieve categories
http://localhost:8081/categories
```
{
"TOP_MAC": "macos-apps/top-mac-apps/all",
"TOP_FREE_MAC": "macos-apps/top-free-mac-apps/all",
"TOP_GROSSING_MAC": "macos-apps/top-grossing-mac-apps/all",
...
```

#### Retrieve apps within category
http://localhost:8081/apps?category=7003
```
[
{
"id": "1291851950",
"appId": "io.voodoo.dune",
"title": "Dune!",
"icon": "http://is1.mzstatic.com/image/thumb/Purple118/v4/36/e8/47/36e847e2-a778-d51a-5f14-89f5394590c4/AppIcon-1x_U007emarketing-85-220-7.png/100x100bb-85.png",
"url": "https://itunes.apple.com/us/app/dune/id1291851950?mt=8&uo=2",
"price": 0,
"currency": "USD",
"free": true,
"description": "Jump above the line to score, but beware! The higher you get, the harder the landing will be! Don't crash and keep it smooth!",
"developer": "Voodoo",
"developerUrl": "https://itunes.apple.com/us/developer/voodoo/id714804730?mt=8&uo=2",
"developerId": "714804730",
"genre": "Games",
"genreId": "6014",
"released": "2017-10-11T05:56:12-07:00",
"version": "1.4"
},
{
...
}
}
```

#### Retrieve common and ucommon features within the given apps
http://localhost:8081/features?ids=1345968745&desc_threshold=75&feature_threshold=75

```{
"comparison": true,
"firstAppName": "McDonald's",
"secondAppName": "Helix Jump",
"commonFeatures": [],
"firstAppFeatures": [
{
"clusterName": "take your money",
"features": [
"take your money",
"pay order",
...
]
},
{
"clusterName": "payments or order",
"features": [
"payments or order",
"process their payment",
...
]
}
...
,
"secondAppFeatures": [
{
"clusterName": "ball feature",
"features": [
"ball feature",
"new ball",
"anticipating new ball"
]
},
{
"clusterName": "game mechanics",
"features": [
"game mechanics",
"game simple mechanics"
]
},
...
}
```

#### Search the apps with search string
http://localhost:8081/searchApp?searchString=messeg
```
[
{
"id": 454638411,
"appId": "com.facebook.Messenger",
"title": "Messenger",
"url": "https://itunes.apple.com/us/app/messenger/id454638411?mt=8&uo=4",
"description": "Instantly connect with the people in your life. ...",
"icon": "https://is4-ssl.mzstatic.com/image/thumb/Purple128/v4/19/b7/69/19b7691b-10e5-530c-fd7e-a54de91d9d6f/source/512x512bb.jpg",
"genres": [
"Social Networking",
"Productivity"
],
"genreIds": [
"6005",
"6007"
],
...
},
{
"id": 447188370,
"appId": "com.toyopagroup.picaboo",
"title": "Snapchat",
"url": "https://itunes.apple.com/us/app/snapchat/id447188370?mt=8&uo=4",
"description": "Life's more fun when you live in the moment :) ..." ,
...
}
]
```

#### Retreieve feature sentiments
http://localhost:8081/sentiments?features=picture%20or%20video,text%20box
```
{
"picture or video": {
"firstFeatures": [
{
"feature": "picture or video",
"frequency": 5
},
...
],
"comparison": false,
"firstAppName": "Messenger",
"firstAppSentimentAverage": 1.14,
"firstAppSentiments": [
{
"sentence": "I thought it was the pictures themselves or the WiFi connection but it happens with any picture or video I try to send, no matter what size, and no matter the WiFi signal strength or network I’m connected to.",
"sentiment": 1
},
{
"sentence": "I'm tired of not being able to adjust my volume during a video call.",
"sentiment": 1
},
... ,
{
"sentence": "You give permission for messenger to listen to, record your voice and video even when messenger or your phone is turned off!",
"sentiment": 1
}
]
},
"text box": {
"firstFeatures": [
{
"feature": "text box",
"frequency": 3
},
...
],
"comparison": false,
"firstAppName": "Messenger",
"firstAppSentimentAverage": 1,
"firstAppSentiments": [
{
"sentence": "Now I have to scroll all the way down to find a REAL text message with someone.",
"sentiment": 1
},
...
]
}
}
```

#### Retrieve app description within the given app
http://localhost:8081/app/description?id=1291851950
```
{
"id": "1291851950",
"description": "Jump above the line to score, but beware! The higher you get, the harder the landing will be! Don't crash and keep it smooth!"
}
```

#### Retreive app details with specific app id
http://localhost:8081/appDetails?appId=454638411

```
{
"id": 454638411,
"appId": "com.facebook.Messenger",
"title": "Messenger",
"url": "https://itunes.apple.com/us/app/messenger/id454638411?mt=8&uo=4",
"description": "Instantly connect with the people in your life. Messenger is free, ...",
"icon": "https://is4-ssl.mzstatic.com/image/thumb/Purple128/v4/19/b7/69/19b7691b-10e5-530c-fd7e-a54de91d9d6f/source/512x512bb.jpg",
"genres": [
"Social Networking",
"Productivity"
],
"genreIds": [
"6005",
"6007"
],
"primaryGenre": "Social Networking",
"primaryGenreId": 6005,
"contentRating": "12+",
"languages": [
"HR",
"CS",
...
],
"size": "235438080",
"requiredOsVersion": "8.0",
"released": "2011-08-09T19:49:28Z",
"updated": "2018-05-03T13:45:49Z",
...
}
```

