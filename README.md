# BookingCom-Reviews-Crawler

This is a project with Scrapy and Selenium combined in order to crawl booking.com site for hotels and their reviews of a pre-specified city. 

## Usage Instructions

1- first of all, make a new python virtual environment.

2- navigate to the virtual env, activate it and clone the repository there.

3- run: pip install -r requirements.txt

4- navigate to ReviewsScraper folder. 

5- open the local terminal and run: scrapy crawl hotels -a city="<name_of_the_city>" -s filename="<file_name>.csv"


## Expected Output: 

1- the named-by-you file will contain hotels information that exist in the named city and booking.com site.

2- plus, a reviews file for each hotel (automatically named, the name is extracted from the hotel link).
