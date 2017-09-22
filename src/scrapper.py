from bs4 import BeautifulSoup
from selenium import webdriver
import urllib2
import cookielib
import pprint
# used to solve unicode error
import sys
import time
import pickle
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
from config import config
reload(sys)
sys.setdefaultencoding('utf8')


all_results_selector = 'a#sln_ps'

first_lot = '.lot.first'

a_ref_lot = 'sln_lot_show'

# get data
# find <button> with Next as value

def login():
    options = webdriver.ChromeOptions()
    options.add_argument('window-size=1200x600')
    driver = webdriver.Chrome(chrome_options=options)
    driver.get('https://www.artprice.com/')
    # bug here have a look and see
    driver.find_element_by_class_name('sln_login_modal').click()

    # wait so the site doesnt think you're a bot
    time.sleep(2)
    driver.find_element_by_id('login').send_keys(config['SECRETS']['username'])
    driver.find_element_by_id('pass').send_keys(config['SECRETS']['password'])
    driver.find_element_by_name('commit').click()
    # wait so the site doesnt think you're a bot
    time.sleep(5)

    ## Move file setup operations outside of the logging in activity
    ## This way its more testable
    
    # pkl_file = open(config['FILENAME'], 'wb')
    # pickle.dump(config['artists'], pkl_file)
    # pkl_file.close()

    print '{}: {}'.format(type(config), config)

    return driver


##
## @brief      { function_description }
##
## @param      artist_sub_path  The artist sub path
## @param      driver           The driver
##
## @return     { description_of_the_return_value }
##
def go_to_artist(artist_sub_path, driver):
    import urlparse
    # go to artists page
    # if bool(urlparse.urlparse(artist_sub_path).netloc):
    #     path = artist_sub_path
    # else:
    path = urlparse.urljoin(config['BASE_URL'], artist_sub_path)
    print path
    driver.get(path)
    # access list of all auctions
    driver.find_element_by_id('sln_ps').click()
    time.sleep(2)


##
## @brief      Gets the artist auction data by entering the actual auction/lots
##             specific page and gathering all the data, this is somewhat
##             deprecated as it was deemed unfeasible.
##
## @param      artist_path  The artist path
## @param      driver       The driver
##
## @return     The artist data.
##
def get_artist_art_pieces(artist_path, driver):
    go_to_artist(artist_path, driver)
    # select first art piece
    first_elm_listed = driver.find_element_by_class_name('first')
    # click into first art piece
    next_button = first_elm_listed.find_element_by_tag_name('a')

    while next_button:
        next_button.click()
        time.sleep(1)
        html = driver.page_source
        # parse art piece info
        headings, artist_data = parse_art_piece(html)
        # filter the data i.e. cleanup the data
        headings = filter_data(headings)
        artist_data = filter_data(artist_data)

        for a, h in zip(artist_data, headings):
            print a
            print h

        # Write data out to file
        pkl_file = open(config['FILENAME'], 'rb')
        out_data = pickle.load(pkl_file)
        pkl_file = open(config['FILENAME'], 'wb')
        out_data[artist_path].append([headings, artist_data, driver.current_url])
        pickle.dump(out_data, pkl_file)
        pkl_file.close()

        # find the next button
        try:
            next_button = driver.find_element_by_xpath("//*[contains(text(), 'Next')]")
        except NoSuchElementException:
            next_button = None
        time.sleep(0.5)


##
## @brief      Gets the artist data from the lots displayed as a paginated list
##             of auction data
##
## @param      artist_path    The artist path
## @param      driver         The selenium driver to use
## @param      data_filename  The file to write the data out to
##
## @return     The artist lots.
##
def get_artist_lots(artist_path, driver, data_filename):
    # go to artist page
    # get to the paginated list of all pieces
    go_to_artist(artist_path, driver)
    next_button = True
    page_count = 0

    pkl_file = open(data_filename, 'rb')
    out_data = pickle.load(pkl_file)
    if artist_path not in out_data.keys():
        out_data[artist_path] = []

    while next_button:
        # need to make this more efficient, timout if page does not load
        # see: https://stackoverflow.com/questions/20819671/python-selenium-does-not-wait-until-page-is-loaded-after-a-click-command
        time.sleep(2)
        html_content = driver.page_source
        # parse content and get relevant data

        lots_from_selenium = driver.find_elements_by_class_name('lot')
        # print html_content

        lots_html = get_art_pieces_short_from_lots(lots_from_selenium)
        # store data
        out_data[artist_path].extend(lots_html)

        # loop to next paginated element
        try:
            next_button = driver.find_element_by_class_name('next_page').find_element_by_tag_name('a')
            # get content for page
        except NoSuchElementException:
            next_button = None
        else:
            next_button.click()

        page_count = page_count+1
        print 'Lot Length: {}\nPage Count: {}'.format(len(lots_html), page_count)

    # Write data out to file
    pkl_file = open(data_filename, 'wb')
    pickle.dump(out_data, pkl_file)
    pkl_file.close()


##
## @brief      Parses art piece information from detailed description of art
##             piece
##
## @param      html_content  e.g. content from selenium driver when calling
##                           page address:
##                           https://www.artprice.com/artist/3363/fernando-botero/drawing-watercolor/11740536/guitare-sur-une-chaise?p=2
##
## @return     headings of the data parsed and the corresponding auction data
##
def parse_art_piece(html_content):
    soup = BeautifulSoup(html_content)
    # identify auction content
    headings = []
    auction_data = []
    for tag in soup.find('div', {'class': 'lot-header'}).find_next_sibling('div').find_next_sibling('div').find_all('div', {'class' : 'marg'}):      
        headings.append(tag.find_next('div').text)
        auction_data.append(tag.find_next('div').find_next('div').text)

    return headings, auction_data


def get_art_pieces_short_from_lots(lots):
    new_lots = []
    for l in lots:
        sp = BeautifulSoup(l.get_attribute('innerHTML'), 'lxml')
        new_lots.append(str(sp.currentTag))

    return new_lots


def filter_data(data):
    import re
    data = [re.findall('\n+ *(.*?)\n', d) for d in data]
    return data

def get_all_artists_data(artists, driver, fname):
    for k, v in artists.iteritems():
        # get the art piece information in listings per artist
        get_artist_lots(k, driver, fname)

def check_all_artist_paths(artists, driver):
    for sub_path in list(artists.keys()):
        go_to_artist(sub_path, driver)

##
## @brief      Gets the list of artists from the user login to parse data from
##
## @param      driver  The selenium driver
##
## @return     The list of artists, which can be used as keys to the dictionary
##
def get_list_of_artists(driver):
    # Go to homepage
    # Get the list of artists
    artist_paths = []
    table = driver.find_element_by_class_name('artists-summary')
    if table.tag_name != 'table':
        raise Exception('Artist list table not found')
    rows = table.find_elements_by_tag_name('tr')
    for r in rows:
        try:
            artist_a_tag = r.find_element_by_tag_name('td').find_element_by_tag_name('a')
        except NoSuchElementException:
            pass
        else:
            artist_path = artist_a_tag.get_attribute('href')
            artist_paths.append(artist_path)
    return artist_paths

def main():
    driver = login()
    # check_all_artist_paths(artists, driver)
    get_all_artists_data(config['artists'], driver, config['FILENAME'])


##
## @brief      Appends new artists to data if artist not present there already
##
## @return     no ret val
##
def append_artists():
    pkl_file = open(config['FILENAME'], 'rb')
    print os.getcwd()

    artists = pickle.load(pkl_file)
    driver = login()
    artist_list = get_list_of_artists(driver)
    print artist_list
    print '----'
    print artists.keys()
    for artist in artist_list:
        if artist not in artists.keys():
            get_artist_lots(artist, driver, config['FILENAME'])



if __name__ == '__main__':
    import os
    os.chdir(config['DATA_PATH'])
    # main()
    # test_filter_data_art_piece()
    # test_parse_short_lot()
    # test_get_artist_data_short()
    # append_artists()
    raise Exception('Proper main thread required')