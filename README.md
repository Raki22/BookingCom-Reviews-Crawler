# BookingCom-Reviews-Crawler

This is a project with Scrapy and Selenium combined in order to crawl booking.com site for hotels and their reviews of a pre-specified city. 

## Usage Instructions

1- first of all, make a new python virtual environment: ``` virtualenv <env_name> ```

2- navigate to the virtual env: ``` cd <env_name> ``` 

3- activate it:  ``` source bin/activate ```

4- clone the repository there: ``` git clone https://github.com/Raki22/BookingCom-Reviews-Crawler ```

5- run:  ``` pip install -r requirements.txt ```

6- navigate to ReviewsScraper folder: ``` cd ReviewsScraper ```

7- open the local terminal and run: ``` scrapy crawl hotels -a city="<name_of_the_city>" -s filename="<file_name>.csv" --loglevel=ERROR ```


## Expected Output: 

1- the named-by-you file will contain hotels information that exist in the named city and booking.com site.

2- plus, a reviews file for each hotel (automatically named, the name is extracted from the hotel link).
