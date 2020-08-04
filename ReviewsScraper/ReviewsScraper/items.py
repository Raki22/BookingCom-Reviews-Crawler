# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class Hotel(Item):
    name = Field()
    stars = Field()
    nbr_of_reviews = Field()
    rating_score = Field()
    rating_label = Field()
    reviews_file = Field()
    hotel_link = Field()


class Review(Item):
    username = Field()
    nationality = Field()
    personal_score = Field()
    review_title = Field()
    positive_part = Field()
    negative_part = Field()
    
