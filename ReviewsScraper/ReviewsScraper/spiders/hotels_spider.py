from scrapy import Spider, Request
from requests import get
from bs4 import BeautifulSoup
from urllib.request import urljoin
from ..items import Hotel
from re import compile
from os import system
import time, logging
from ..serializers import *
from ..reviews_selenium_crawl import main as parse_reviews

class HotelsSpider(Spider):
    name = "hotels"
    city = ''
    def __init__(self, city):
        self.city = city

    def start_requests(self):
        urls = [get("https://www.booking.com/searchresults.ar.html", params={'ss': self.city}).url]
        for url in urls:
            yield Request(url, self.parse)

    def parse(self, response):
        def getHotelName(hotelDiv):
            try:
                name = hotelDiv.find('h3', {'class':"sr-hotel__title"}).find('span', {'class':"sr-hotel__name"}).get_text()
            except AttributeError:
                name = ''
            return serialize_name(name)

        def getHotelLink(hotelDiv):
            ptrn = compile(r'#hotelTmpl')
            try:
                link = hotelDiv.find('h3', {'class':"sr-hotel__title"}).find('a', {'class':["hotel_name_link", "url"]}).attrs['href']
                link = ptrn.sub("#tab-reviews", link).strip(" \n")
            except AttributeError:
                link = ''
            return link

        def getHotelStars(hotelDiv):
            try:
                stars = hotelDiv.find('span', {'class':"sr-hotel__title-badges"}).find('i', {'class':["bk-icon-wrapper", "bk-icon-stars", "star_track"]}).attrs['title']
            except AttributeError:
                try:
                    stars = len(hotelDiv.find('span', {'class':"sr-hotel__title-badges"}).find('span', {'class':["bh-quality-bars", "bh-quality-bars--medium"]}).find_all('svg', {'class':["bk-icon", "-iconset-square_rating"]}))
                except AttributeError:
                    stars = ''
            return serialize_stars(stars)

        def getNbrOfReviews(hotelDiv):
            try:
                nbr = hotelDiv.find('div', {'class':"bui-review-score__content"}).find('div', {'class':"bui-review-score__text"}).get_text()
            except AttributeError:
                nbr = ''
            return serialize_nbrReviews(nbr)

        def getRating(hotelDiv):
            try:
                ratingLabel = hotelDiv.find('div', {'class':"bui-review-score__content"}).find('div', {'class':"bui-review-score__title"}).get_text()
                ratingScore = hotelDiv.find('div', {'class':"bui-review-score__badge"}).get_text()
            except AttributeError:
                ratingLabel = ''
                ratingScore = ''
            return (serialize_ratingLabel(ratingLabel), serialize_ratingScore(ratingScore))

        def getHotelPages(soupObject):
            try:
                lis = soupObject.find('nav', {'class':"bui-pagination__nav"}).find('li', {'class':"bui-pagination__pages"}).find('ul', {'class':"bui-pagination__list"}).find_all('li', {'class':["bui-pagination__item", "sr_pagination_item"]})
            except AttributeError:
                lis = []
            if lis != []:
                links = []
                for li in lis:
                    try:
                        links.append(urljoin("https://www.booking.com/", li.a.attrs['href']))
                    except AttributeError:
                        continue
                return links

        logger = logging.getLogger('reviews_crawl')
        hdlr = logging.FileHandler('./reviews_crawl.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr) 
        logger.setLevel(logging.INFO)
        soup = BeautifulSoup(response.body, "html.parser")
        hotelsList = soup.find('div', {'id':"hotellist_inner"}).find_all('div', {'class':["sr_item", "sr_item_new", "sr_item_default", "sr_property_block", "sr_flex_layout", "sr_item_no_dates"]})
        log_file = open("./reviews_crawl.log", 'r')
        for hotelDiv in hotelsList:
            hotel = Hotel()
            hotel['name'] = getHotelName(hotelDiv) 
            hotel['stars'] = getHotelStars(hotelDiv)
            hotel['nbr_of_reviews'] = getNbrOfReviews(hotelDiv)
            hotel['rating_score'] = getRating(hotelDiv)[1]
            hotel['rating_label'] = getRating(hotelDiv)[0]
            hotel['hotel_link'] = urljoin("https://www.booking.com/", getHotelLink(hotelDiv))
            if hotel['hotel_link'] in log_file.read():
                continue
            else:
                hotel['reviews_file'] = parse_reviews(hotel['hotel_link'])
                logger.info("{} has been crawled for reviews successfully".format(hotel['hotel_link']))
                yield hotel
                

        yield from response.follow_all(getHotelPages(soup), callback=self.parse)
        log_file.close()