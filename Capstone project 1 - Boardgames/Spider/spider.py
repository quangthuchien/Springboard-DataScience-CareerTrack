import re
import time
from bs4 import BeautifulSoup
from boardgamegeek import BGGClient
import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.item import Item, Field
# from selenium.common.exceptions import NoSuchElementException
# pip install boardgamegeek2 to install boardgameGeek
#I have used selenium to scrape using XPATH
from selenium import webdriver

gameurl='https://boardgamegeek.com/boardgame/'
bgg = BGGClient()

#based on the platform download phantomjs and give the path to the the executable
browser = webdriver.PhantomJS(executable_path=r'/Users/quangthuchien/datascienceclass/Capstone\ project\ 1\ -\ Boardgames/Spider/phantomjs.exe')
#browser = webdriver.PhantomJS() #phantomjs.exe has to be in the same directory with this script

class Game(Item):
    id = Field()
    title = Field()
    geek_rate = Field()
    avg_rate = Field()
    num_votes = Field()
    type=Field()
    yearpublished=Field()
    minplayers=Field()
    maxplayers=Field()
    playingtime=Field()
    minplaytime=Field()
    maxplaytime=Field()
    minage=Field()
    usersrated=Field()
    bayesaverage=Field()
    classificationtype=Field()
    category=Field()
    mechanism=Field()
    family=Field()
    #you can add additional attributes as Field() it will automaticallly create column in CSV


    # ID, type(boardgame / boardgame
    # expansion), yearpublished, minplayers, max
    # players, playingtime, minplaytime, maxplaytime, minage, usersrated, average
    # rating, bayesaverage, type(family, abstract, thematics, etc...), categories, mechanism, family

class GameSpider(CrawlSpider):
    name = 'boardgamegeek_spider'
    allowed_domains = ['boardgamegeek.com']
    start_urls = ['http://www.boardgamegeek.com/browse/boardgame']
    custom_settings = {'DOWNLOAD_DELAY': 1, 'BOT_NAME': 'Mr. Scraper Bot'}

    #importing basic game information like id name
    def parse(self, response):
        soup = BeautifulSoup(response.body, 'lxml')

        next_page = soup.select('a[title^="next"]')
        if next_page:
            next_page = next_page[0].get('href')
        if next_page:
            yield self.make_requests_from_url(response.urljoin(next_page))
        rows = soup.select('tr#row_')
        for row in rows:
            g = Game()
            a = row.find_all('a', href=re.compile('^/boardgame'))
            for r in a:
                if r.text:
                    g['id'] = r.get('href').split('/')[2]
                    g['title'] = r.text
            geek_rate, avg_rate, num_votes = row.select('td.collection_bggrating')
            g['geek_rate'] = geek_rate.text.strip()
            g['avg_rate'] = avg_rate.text.strip()
            g['num_votes'] = num_votes.text.strip()
            thisgameurl=gameurl+g['id']
            print (thisgameurl)


            browser.get(thisgameurl) #using selenium to scrape the webpage

            # get game types
            elem = browser.find_element_by_xpath(
                '//*[@id="mainbody"]/div/div[1]/div[1]/div[2]/ng-include/div/div/ui-view/ui-view/div[1]/overview-module/description-module/div/div[2]/div/div[1]/classifications-module/div/div[2]/ul/li[1]/div[2]')
            types = elem.find_elements_by_tag_name('span')
            game_types = ''
            # print '\ngame type\n'


            for eachtype in types:
                 game_types = game_types + eachtype.text
                       # individual=eachtype.find_element_by_tag_name('a')
                    # print individual.text

            game_types = game_types.replace(', ,', ',')
            g['classificationtype']=game_types


            #The code below is an alternative way to extract the categories and families using selenuim and XPATH, found a better way therefore commented it
            # category
            # elem = browser.find_element_by_xpath(
            #     '//*[@id="mainbody"]/div/div[1]/div[1]/div[2]/ng-include/div/div/ui-view/ui-view/div[1]/overview-module/description-module/div/div[2]/div/div[1]/classifications-module/div/div[2]/ul/li[2]/div[2]/popup-list')
            # categories = elem.find_elements_by_class_name('text-block')
            # categories_type = ''
            # # print '\ncategories\n'
            #
            #
            # try:
            #     for eachtype in categories:
            #         categories_type = categories_type + eachtype.text + ','
            #         # individual=eachtype.find_element_by_tag_name('a')
            #         # print individual.text
            # except NoSuchElementException as e:
            #     pass
            #
            # # mechanism
            # elem = browser.find_element_by_xpath(
            #     '//*[@id="mainbody"]/div/div[1]/div[1]/div[2]/ng-include/div/div/ui-view/ui-view/div[1]/overview-module/description-module/div/div[2]/div/div[1]/classifications-module/div/div[2]/ul/li[3]/div[2]/popup-list')
            # mechanisms = elem.find_elements_by_class_name('text-block')
            # mechanism_type = ''
            # # print '\n mechanism \n'
            # try:
            #     for eachtype in mechanisms:
            #         mechanism_type = mechanism_type + eachtype.text + ','
            #         # individual=eachtype.find_element_by_tag_name('a')
            #         # print individual.text
            # except NoSuchElementException as e:
            #     pass
            #
            #
            # # family
            # elem = browser.find_element_by_xpath(
            #     '//*[@id="mainbody"]/div/div[1]/div[1]/div[2]/ng-include/div/div/ui-view/ui-view/div[1]/overview-module/description-module/div/div[2]/div/div[1]/classifications-module/div/div[2]/ul/li[4]/div[2]/popup-list')
            # families = elem.find_elements_by_class_name('text-block')
            # family_type = ''
            # # print '\n family \n'
            # try:
            #     for eachtype in families:
            #         family_type = family_type + eachtype.text + ','
            # except NoSuchElementException as e:
            #     pass

            bgggame = bgg.game(game_id=int(g['id']))#it uses the boardgame geek libraryy to get info of the game given the id
            g['family']=bgggame.families
            g['type']='boardgame'
            g['yearpublished']=bgggame.year
            g['minplayers'] = bgggame.min_players
            g['maxplayers'] =bgggame.max_players
            g['playingtime'] = bgggame.playing_time
            g['minplaytime'] = bgggame.min_playing_time
            g['maxplaytime'] = bgggame.max_playing_time
            g['minage'] = bgggame.min_age
            g['usersrated'] = bgggame.users_rated
            g['bayesaverage'] = bgggame.rating_bayes_average
            g['category'] = bgggame.categories
            g['mechanism'] = bgggame.mechanics

            # you can add many other informations which are not used yet like
            yield g
