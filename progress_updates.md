## 21 Dec 2020
- Now it's possible to fetch multiple `app_id` for both Google Play Store and Apple App Store
- Added multiple country code for Apple App Store only
- Updated library `google-play-scraper` to v0.1.2

## 4 Dec 2020
- Finished feature extraction from the remaining top 10 ridesharing apps
- Found [available tools](https://mast.informatik.uni-hamburg.de/app-review-analysis/) related to paper references about feature extraction from app description and app reviews
- Found [documentation](https://mast.informatik.uni-hamburg.de/wp-content/uploads/2016/08/Coding-Guide-V8_Final.pdf) related to automatic review analysis
- Test Google Translate Document Translation using .xls file, and manually export it into Excel file

## 30 Nov 2020
- Added all top 10 app id for both app store and play store
- All csv output can be accessed from [Google Drive]
- Added `progress_updates.md` to track my thesis progress

## 20 Nov 2020
- Added review mining result for Uber. Spreadsheet from here (sheet name uber_ee_google_playstore_review and uber_gb_apple_appstore_review)
- Updated python code for review mining, now using yaml config file to store meta data (app_id, country_code, etc)
- example of config yaml file: [config.yaml]
- Added functional and non-functional requirement for ridesharing app. [spreadsheet]

## 13 Nov 2020
- Finding “top 10 European ride sharing applications”
  - Check the [spreadsheet]
  - Due to some restriction, I can’t get Apple App Store total downloads and latest update date
  - It was available in AppAnnie, but it needs AppAnnie premium account
  - I will add description and available countries later
- Update review mining for App Store
  - Now exporting to .csv file (instead of .xlsx)
  - Added Apple App Store review mining for Bolt app, [jupyter_appstore]
  - Import the csv result into main [spreadsheet]


[spreadsheet]: https://docs.google.com/spreadsheets/d/1ESxdtyBuml5Q3zm0r3KkbBQVkiPV9sQpw0fqAN5kXmc/edit?usp=sharing
[jupyter_appstore]: https://github.com/enliktjioe/master-thesis-2021/blob/main/review_mining/ReviewMining_app-store-scraper.ipynb
[jupyter_playstore]: https://github.com/enliktjioe/master-thesis-2021/blob/main/review_mining/ReviewMining_google-play-scraper.ipynb
[config.yaml]: https://github.com/enliktjioe/master-thesis-2021/blob/main/review_mining/config.yaml
[Google Drive]: https://drive.google.com/drive/folders/1OepRslaRdsdnPP5pPy3kl8pC6NntqBi-?usp=sharing