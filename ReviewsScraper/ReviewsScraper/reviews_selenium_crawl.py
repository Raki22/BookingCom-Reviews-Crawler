from sys import argv
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, MoveTargetOutOfBoundsException
from bs4 import BeautifulSoup
import time
from .serializers import *
from csv import DictWriter
from re import compile, sub
from urllib.request import urljoin


def reviewsCollector(soupObject):
    try:
        return soupObject.find('div', {'id':'review_list_page_container'}).find('ul', {'class':'review_list'}).find_all('li', {'class':'review_list_new_item_block'})
    except AttributeError:
        print("\t the spider didn't find any reviews in this page")
    

def reviewsFileFiller(reviewsList, outputFileName, _filter, link):
    try:
        reviewsList = list(set(reviewsList))
    except TypeError:
        reviewsList = []
    if reviewsList != []:
        reviews_file = open(outputFileName, 'w')
        csvWrite = DictWriter(reviews_file, fieldnames=['username', 'nationality', 'personal_score', 'review_title', 'positive_part', 'negative_part'], delimiter='\t')
        csvWrite.writeheader()
        pattern = compile(r'[\u0600-\u06FF]*')
        for reviewLi in reviewsList:
            review = {}
            review['username'] = getUserName(reviewLi)
            review['nationality'] = getNationality(reviewLi)
            review['personal_score'] = getPersonalScore(reviewLi)
            review['review_title'] = getReviewTitle(reviewLi)
            review['positive_part'] = getReviewParts(reviewLi)[0]
            review['negative_part'] = getReviewParts(reviewLi)[1]
            if _filter and (pattern.search(review['review_title']) == None) and (pattern.search(review['positive_part']) == None) and (pattern.search(review['negative_part']) == None):
                continue
            else:  
                csvWrite.writerow(review)
        reviews_file.close()
    else:
        print("\t this hotel has no reviews")

def getNbrOfReviewPages(driver):
    numbers = driver.find_elements_by_xpath('//div[@id="review_list_page_container"]//div[@class="bui-pagination__nav" and @role="navigation"]//div[@class="bui-pagination__pages"]/div[@class="bui-pagination__list"]/div[@class="bui-pagination__item "]/a[@class="bui-pagination__link"]/span[@aria-hidden="true"]')
    try:
        lastPage = max([int(nbr.get_attribute('innerText')) for nbr in numbers])
    except ValueError:
        lastPage = 1
    if lastPage < 2:
        return "\t this hotel has just one page of reviews"
    else:
        return lastPage + 1

def nextPageClicker(driver, pageNumber):
    wait = WebDriverWait(driver, 7)
    nextPageButton_path = '//div[@id="review_list_page_container"]//div[@class="bui-pagination__list"]/div[@class="bui-pagination__item "]/a[@class="bui-pagination__link"  and ./span[@aria-hidden="true"]/text()="{}"]'.format(pageNumber)
    nextPageButton = wait.until(EC.element_to_be_clickable((By.XPATH, nextPageButton_path)))
    actions = ActionChains(driver)
    driver.execute_script("document.evaluate('{}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.scrollIntoView();".format(nextPageButton_path))
    actions.move_to_element(nextPageButton)
    actions.click()
    try:
        actions.perform()
    except MoveTargetOutOfBoundsException:
        print("\t\t The element took a long time to be in the viewport !")
    
    return driver

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



######################################### main act ###############################################


def main(hotelLink, browser, filterNonArabic = False):        
    url = urljoin(hotelLink, "#tab-reviews")
    print("parsing {} for reviews".format(url))
    pattern = compile(r'/[a-zA-Z0-9\-]*\.ar\.html')
    fileName = sub(r'(/|.ar.html)', '', pattern.findall(hotelLink)[0]) + ".csv"
    if browser == 'firefox':
        options = FirefoxOptions()
        options.headless = True
        driver = webdriver.Firefox(options=options)
    elif browser == 'chrome':
        options = ChromeOptions()
        options.headless = True
        driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)    
    except TimeoutException:
        raise Exception("please check your Internet Connection")
    time.sleep(7)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    reviewsList = reviewsCollector(soup)
    nbrOfPages = getNbrOfReviewPages(driver)
    if type(nbrOfPages) is int:
        print("\t found {} review pages to crawl".format(nbrOfPages - 1))
        for i in range(2, nbrOfPages):
            print("\t\t parsing reviews page number {}".format(i))
            driver = nextPageClicker(driver, i)
            time.sleep(5)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            reviewsList.extend(reviewsCollector(soup))
    else:
        print(nbrOfPages)

    reviewsFileFiller(reviewsList, fileName, filterNonArabic, hotelLink)
    driver.quit()
    return fileName