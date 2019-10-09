# Kink Scraper
So ... having extensive kink.com collection, that I want to add to KODI. There is no good provider for scraping the internet and building the DB. 
So I created this little thingy. Just start scraper.py and you will get simple interface that allows you to select the folder where your collection is and start adding scrapin one by one.
The application allows the files to be moved in separate directory with the same name as the file.

## What is workin
1. Select movie and try to guess movie ID
2. Alow search for movies from kink.com
3. Scrape information 
4. Write NFO with the name of the folder
5. Move files to folder with the same name

## TODO
1. Allow application to rename movies and folders in specific format ({CHANNEL} {DATE} {NAME} ({ID}))
2. Get fanart.

## Run
python scraper.py

## Requires
The following Python libraries are required to work:
1. lxml
2. requests
3. wxPython
