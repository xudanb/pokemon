"""
* implements a scrapy crawl spider that starts from a set of page urls, scrapes 
* information contained in the individual card urls, parses information, stores 
* parsed information as card items and feed exports items into a csv file

* usage: scrapy crawl pokemon -o csvfilepath
* author: xudanb
"""

# import scrapy and dependencies
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy import Selector

# import selenium and dependencies
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# import item for storing individual card information
from pokemon.items import CardItem

import time

class PokemonSpider(CrawlSpider):
    """
    * main scrapy crawl spider class
    """
    # identifier
    name = "pokemon" 
    # specifies range of page numbers to scrape, page number in [start, end]
    start, end = 1, 1
    start_urls = ["https://www.tcgcollector.com/cards/intl?page="+str(i) for i in range(start, end+1)]
    # specifies rules for recursively scraping individual card pages
    rules = [
        Rule(LinkExtractor(allow=r"https://www.tcgcollector.com/cards/\d+"), callback='parse_card'), 
        # rule for following to next page, not used here
        # Rule(LinkExtractor(restrict_xpaths="//li[@class='pagination-item pagination-item-next ']"), follow=True)
    ]
    # initialize webdriver for scraping dynamic content
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    # login credentials for website
    email, password = "", ""
    # sign in to website to access hidden information
    driver.get ("https://www.tcgcollector.com/account/sign-in")
    driver.find_element_by_id("sign-in-email-address").send_keys(email)
    driver.find_element_by_id ("sign-in-password").send_keys(password)
    driver.find_element_by_xpath("//button[@type='submit']").click()

    def parse_card(self, response):
        """
        * function for parsing individual cards information, storing to items, 
        * and exporting to feed
        """
        # parse 'upper' portion of each card page
        # initialize to empty strings
        name, hp, energy, card_type, evolution, evolved_from = "", "", "", "", "", ""
        # parse name
        matches = response.xpath("//div[@id='card-info-title-container']")
        if len(matches)>0:
            match = matches[0].xpath('h1/text()').extract()
            if len(match)>0:
                name = match[0].strip()
        # parse hp
        matches = response.xpath("//div[@id='card-hit-points-container']")
        if len(matches)>0:
            match = matches[0].xpath('a/text()').extract()
            if len(match)>0:
                hp = match[0].strip()
        # parse energy
        matches = response.xpath("//a[@id='card-energy-types']")
        if len(matches)>0:
            match = matches[0].xpath('img/@title').extract()
            if len(match)>0:
                energy = match[0].strip()
        # parse card type, multiple types possible
        matches = response.xpath("//span[@class='card-type-container']/text()").extract()
        if len(matches)>0:
            card_type = "".join([t.strip() for t in matches])
        # parse evolution & evolved_from
        matches = response.xpath("//div[@id='card-evolution-status']/a")
        if len(matches)>0:
            match = matches[0].xpath('text()').extract()
            if len(match)>0:
                evolution = match[0].strip()
        if len(matches)>1:
            match = matches[1].xpath('em/text()').extract()
            if len(match)>0:
                evolved_from = match[0].strip()

        # parse 'upper' portion of each card page
        # initialize attack names and attack damages to empty lists
        atks, dmgs = [], []
        for match in response.xpath("//div[@class='card-attack-header-text']"):
            temp1 = match.xpath('h3/text()').extract()
            temp2 = match.xpath('span/text()').extract()
            # if both attack name and attack damage are not empty, append them 
            # seperately to the two lists
            if len(temp1)>0 and len(temp2)>0:
                atks.append(temp1[0].strip())
                dmgs.append(temp2[0].strip())
            # otherwise if attack name is not empty, append it to attack names 
            # list and append "0" to attack damages list
            elif len(temp1)>0:
                atks.append(temp1[0].strip())
                dmgs.append("0")
        # join attack names and attack damages lists to get single strings
        attacks, damages = ";".join(atks), ";".join(dmgs)

        # parse 'bottom' portion of each card page
        # initialize to empty strings
        weakness, resistance, retreat_cost, expansion = "", "", "", ""
        card_number, rarity, card_format, illustrators = "", "", "", ""
        # iterate through all the card info items
        for match in response.xpath("//div[@class='card-info-footer-item']"):
            # extract item category
            category = match.xpath('h3/text()').extract()
            if len(category)>0:
                # update different fields depending on category
                if category[0]=="Weakness":
                    weak_type, weak_mult = "", ""
                    temp = match.xpath('a/div/img/@title').extract()
                    if len(temp)>0:
                        weak_type = temp[0].strip()
                    temp = match.xpath('a/div/span/text()').extract()
                    if len(temp)>0:
                        weak_mult = temp[0].strip()
                    weakness = weak_type+weak_mult
                elif category[0]=="Resistance":
                    resist_type, resist_mult = "", ""
                    temp = match.xpath('a/div/img/@title').extract()
                    if len(temp)>0:
                        resist_type = temp[0].strip()
                    temp = match.xpath('a/div/span/text()').extract()
                    if len(temp)>0:
                        resist_mult = temp[0].strip()
                    resistance = resist_type+resist_mult
                elif category[0]=="Retreat Cost":
                    temp = match.xpath('a/img').extract()
                    retreat_cost = len(temp)
                elif category[0]=="Expansion":
                    temp = match.xpath('div/a/text()').extract()
                    if len(temp)>0:
                        expansion = temp[0].strip()
                elif category[0]=="Card number":
                    temp = match.xpath('div/span/text()').extract()
                    if len(temp)>0:
                        card_number = temp[0].strip()
                elif category[0]=="Rarity":
                    temp = match.xpath('div/a/text()').extract()
                    if len(temp)>0:
                        rarity = temp[0].strip()
                # card format can only have one value, so only one of the 
                # following two groups of statements will update the 
                # card_format variable
                elif category[0]=="Card format":
                    # unlimited
                    temp = match.xpath('div/span/text()').extract()
                    if len(temp)>0:
                        card_format = temp[0].strip()
                    # standard/expanded
                    temp = match.xpath('div/a/text()').extract()
                    if len(temp)>0:
                        card_format = temp[0].strip()
                elif category[0]=="Illustrators":
                    temp = match.xpath('div/span/a/text()').extract()
                    if len(temp)>0:
                        illustrators = temp[0].strip()

        # parse dynamic content of each card page
        # initialize to empty strings
        variants, languages = "", ""
        # call webdriver, find the button with three little dots, click on it
        self.driver.get(response.url)
        self.driver.find_element_by_xpath("//button[@class='card-collection-card-modal-button']").click()
        # wait 0.1 second for dynamic content to load (bad practice, will 
        # update in the future)
        time.sleep(0.1)
        # cast response text to scrapy selector and parse information as needed
        matches = Selector(text=self.driver.page_source).xpath("//div[@class='form-field']/select")
        if len(matches)>0:
            temp = matches[0].xpath("option/text()").extract()
            variants = ";".join([l.strip() for l in temp])
        if len(matches)>1:
            temp = matches[1].xpath("option/text()").extract()
            languages = ";".join([l.strip() for l in temp])

        # store all parsed fields into a card item
        card = CardItem()
        card['name'], card['hp'], card['energy'] = name, hp, energy
        card['card_type'], card['evolution'], card['evolved_from'] = card_type, evolution, evolved_from
        card['attacks'], card['damages'] = attacks, damages
        card['weakness'], card['resistance'], card['retreat_cost'], card['expansion'] = weakness, \
            resistance, retreat_cost, expansion
        card['card_number'], card['rarity'], card['card_format'], card['illustrators'] = card_number, \
            rarity, card_format, illustrators
        card['variants'], card['languages'] = variants, languages

        # export generated item to feed
        yield card