from scrapy import Spider, Request
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from ..items import Review
from ..serializers import *
import time


class ReviewsSpider(Spider):
    name = "reviews"
    hotelLink = ''

    def __init__(self, hotel_link):
        self.hotelLink = hotel_link

    start_urls = [hotelLink]

    def parse(self, response):
        def getUserName(reviewLi):
            try:
                name = reviewLi.find('div', {'class':["c-guest", "bui-avatar-block"]}).find('div', {'class':"bui-avatar-block__text"}).find('span', {'class':"bui-avatar-block__title"}).get_text()
            except AttributeError:
                name = ''
            return name

        def getNationality(reviewLi):
            try:
                nationality = reviewLi.find('div', {'class':["c-guest", "bui-avatar-block"]}).find('div', {'class':"bui-avatar-block__text"}).find('span', {'class':"bui-avatar-block__subtitle"}).get_text()
            except AttributeError:
                nationality = ''
            return serialize_nationality(nationality)

        def getPersonalScore(reviewLi):
            try:
                score = reviewLi.find('div', {'class':"c-guest-with-score__score"}).find('div', {'class':"bui-review-score__badge"}).get_text()
            except AttributeError:
                score = ''
            return score

        def getReviewTitle(reviewLi):
            try:
                title = reviewLi.find('h3', {'class':["c-review-block__title", "c-review-block__title--original", "c-review__title--rtl"]}).get_text()
            except AttributeError:
                title = ''
            return serialize_reviewTitle(title)

        def getReviewParts(reviewLi):
            try:
                parts = reviewLi.find_all('p', {'class':"c-review__inner"})
            except AttributeError:
                parts = []
            if parts == []:
                return ('', '')
            elif len(parts) == 2:
                positive = parts[0].find('span', {'class':["c-review__body", "c-review__body--original"]}).get_text()
                negative = parts[1].find('span', {'class':["c-review__body", "c-review__body--original"]}).get_text() 
                return (serialize_positivePart(positive), serialize_negativePart(negative))
            elif len(parts) == 1:
                try:
                    emotionIdentifier = parts[0].find('span', {'class':"c-review__prefix"}).find('span', {'class':"bui-u-sr-only"}).get_text().strip(" \n")
                except AttributeError:
                    emotionIdentifier = None
                if emotionIdentifier == None:
                    return ('', '')
                else:
                    if emotionIdentifier == "نال الإعجاب":
                        positive = parts[0].find('span', {'class':["c-review__body", "c-review__body--original"]}).get_text() 
                        return (serialize_positivePart(positive), '')
                    elif emotionIdentifier == "لم ينل الإعجاب":
                        negative = parts[0].find('span', {'class':["c-review__body", "c-review__body--original"]}).get_text()
                        return ('', serialize_negativePart(negative))


        url = self.hotelLink
        options = FirefoxOptions()
        options.headless = True
        driver = webdriver.Firefox(options=options)
        driver.get(url)
        time.sleep(7)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        reviewsList = soup.find('div', {'id':'review_list_page_container'}).find('ul', {'class':'review_list'}).find_all('li', {'class':'review_list_new_item_block'})
        reviewPages = driver.find_elements_by_xpath('//div[@id="review_list_page_container"]//div[@class="bui-pagination__nav" and @role="navigation"]//div[@class="bui-pagination__pages"]/div[@class="bui-pagination__list"]/div[@class="bui-pagination__item "]/a[@class="bui-pagination__link"]')
        for a in reviewPages:
            driver.get(a.get_attribute('href'))
            # time.sleep(5)
            pseudo_soup = BeautifulSoup(driver.page_source, "html.parser")
            reviewsList.extend(pseudo_soup.find('ul', {'class':'review_list'}).find_all('li', {'class':'review_list_new_item_block'}))
        reviewsList = list(set(reviewsList))
        for reviewLi in reviewsList:
            review = Review()
            review['username'] = getUserName(reviewLi)
            review['nationality'] = getNationality(reviewLi)
            review['personal_score'] = getPersonalScore(reviewLi)
            review['review_title'] = getReviewTitle(reviewLi)
            review['positive_part'] = getReviewParts(reviewLi)[0]
            review['negative_part'] = getReviewParts(reviewLi)[1]
            yield review