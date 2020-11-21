import scrapy
from scrapy.item import Item, Field

class CardItem(scrapy.Item):
    # defines the card item class for storing parsed information
    name = scrapy.Field()
    hp = scrapy.Field()
    energy = scrapy.Field()
    card_type = scrapy.Field()
    evolution = scrapy.Field()
    evolved_from = scrapy.Field()
    attacks = scrapy.Field()
    damages = scrapy.Field()
    weakness = scrapy.Field()
    resistance = scrapy.Field()
    retreat_cost = scrapy.Field()
    expansion = scrapy.Field()
    card_number = scrapy.Field()
    rarity = scrapy.Field()
    card_format = scrapy.Field()
    illustrators = scrapy.Field()
    variants = scrapy.Field()
    languages = scrapy.Field()