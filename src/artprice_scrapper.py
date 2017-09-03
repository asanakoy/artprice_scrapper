from bs4 import BeautifulSoup
from selenium import webdriver
import urllib2
import cookielib
import pprint
#used to solve unicode error
import sys  
import time
import pickle
from selenium.common.exceptions import NoSuchElementException
reload(sys)  
sys.setdefaultencoding('utf8')

import pandas as pd
# Constant variables
artists = {
    "/artist/144730/beatriz-gonzalez/": [],
    "/artist/140609/jorge-cavelier/" : [],
    "/artist/135880/carlos-rojas/" : [],
    "/artist/21426/alejandro-obregon/" : [],
    "/artist/23813/eduardo-ramirez-villamizar/" : [],
    "/artist/23957/omar-rayo/" : [],
    "/artist/20967/edgar-negret/" : [],
    "/artist/145472/doris-salcedo/" :[],
    "/artist/3363/fernando-botero/" : [],
    "/artist/36340/margarita-lozano/" : []
}

TEMPLATE_LOT = {
       'lot': None, #int
       'address': None, # relative path to the lot for more info
       'image': None, # url
       'title': None, # string Title of the art piece (a {'title'})
       'date': None, # year drawn
       'type': None, # (str) Painting type
       'size': None, # (zip(int))size in string width x height
       'estimate_price': None, # (lower, upper) price in USD
       'hammer_price': None, # int
       'auction_house': [] # [name, location]
       }

BASE_URL = "https://www.artprice.com/"
FILENAME = 'data_full_test.pickle'
OUTFILENAME = 'data_output.xlsx'
CSV_FILENAME = 'output.csv'

all_results_selector = 'a#sln_ps'

first_lot = '.lot.first'

a_ref_lot = 'sln_lot_show'

# get data
# find <button> with Next as value
# 
# 

def login():
    options = webdriver.ChromeOptions()
    options.add_argument('window-size=1200x600')
    driver = webdriver.Chrome(chrome_options=options)
    driver.get('https://www.artprice.com/')
    #bug here have a look and see
    driver.find_element_by_class_name('sln_login_modal').click()

    # wait so the site doesnt think you're a bot
    time.sleep(2)
    driver.find_element_by_id('login').send_keys('ameliapradillag@hotmail.com')
    driver.find_element_by_id('pass').send_keys('revolutioN1')
    driver.find_element_by_name('commit').click()
    # wait so the site doesnt think you're a bot
    time.sleep(2)
    
    pkl_file = open(FILENAME, 'wb')
    pickle.dump(artists, pkl_file)
    pkl_file.close()
    
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
    path = urlparse.urljoin(BASE_URL, artist_sub_path)
    print path
    driver.get(path)
    # access list of all auctions
    driver.find_element_by_id('sln_ps').click()
    time.sleep(2)

##
## @brief      Gets the artist data.
##
## @param      artist_path  The artist path
## @param      driver       The driver
##
## @return     The artist data.
##
def get_artist_data(artist_path, driver):
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
            
        #Write data out to file
        pkl_file = open(FILENAME, 'rb')
        out_data = pickle.load(pkl_file)
        pkl_file = open(FILENAME, 'wb')
        out_data[artist_path].append([headings, artist_data, driver.current_url])
        pickle.dump(out_data, pkl_file)
        pkl_file.close()
        
        # find the next button
        try:
            next_button = driver.find_element_by_xpath("//*[contains(text(), 'Next')]")
        except NoSuchElementException:
            next_button = None
        time.sleep(0.5)


def get_artist_data_short(artist_path, driver, data_filename):
    # go to artist page
    # get to the paginated list of all pieces
    go_to_artist(artist_path, driver)
    next_button = True
    page_count = 0

    pkl_file = open(data_filename, 'rb')
    out_data = pickle.load(pkl_file)
    while next_button:
        # need to make this more efficient, timout if page does not load
        # see: https://stackoverflow.com/questions/20819671/python-selenium-does-not-wait-until-page-is-loaded-after-a-click-command
        time.sleep(2)
        html_content = driver.page_source
        # parse content and get relevant data
        
        #lots, soup = get_art_pieces_short(html_content)
        lots = driver.find_elements_by_class_name('lot')
        #print html_content
        
        lots = get_art_pieces_short_from_lots(lots)
        # store data
        out_data[artist_path].extend(lots)

        # loop to next paginated element
        try:
            next_button = driver.find_element_by_class_name('next_page').find_element_by_tag_name('a')
            # get content for page
        except NoSuchElementException:
            next_button = None
        else:
            next_button.click()

        page_count = page_count+1
        print 'Lot Length: {}\nPage Count: {}'.format(len(lots), page_count)
    
    #Write data out to file
    pkl_file = open(data_filename, 'wb')
    pickle.dump(out_data, pkl_file)
    pkl_file.close()

##
## @brief      Parses art piece information from detailed description of art
##             piece
##
## @param      html_content  e.g. content from selenium driver when calling page
##                           address:
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


def get_art_pieces_short(html_content):
    # parses the data available from the list without clicking into the art piece
    # 1. parses the data listed
    # 2. parses the image link url
    # 3. parses the url to the more detailed page
    soup = BeautifulSoup(html_content, 'lxml')
    lots = soup.find_all('div', {'class': 'lot'})
    # return the lots as beautiful soup elements
    return lots, soup

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


def parse_short_lot(lot):
    out_lot = TEMPLATE_LOT
    soup = BeautifulSoup(lot, 'lxml')
    divs = soup.div.find_all('div')
    out_lot['lot'] = divs[0].p.text
    out_lot['address'] = str(divs[2].a['href']), # relative path to the lot for more info
    out_lot['image'] = divs[2].img['src'], # url
    out_lot['title'] = str(soup.find(attrs={'title': True})['title']), # string Title of the art piece (a {'title'})
    
    for div in soup.findAll('div'):
        if div.date:
            main_div = div
            break
    
    out_lot['date'] = main_div.date.text, # year drawn
    
    
    pars = main_div.find_all('p')
    type_and_size = pars[1].text
    #@todo needs to be parsed
    out_lot['type'] = None  # (str) Painting type
    out_lot['size'] = None  # (zip(int))size in string width x height
    
    # get price estimates
    for span in pars[3].find_all('span', {'ng-show': True}):
        if 'USD' in span['ng-show']:
            out_lot['estimate_price'] = span.text
    
    # get hammer price
    for span in pars[4].find_all('span', {'ng-show': True}):
        if 'USD' in span['ng-show']:
            out_lot['hammer_price'] = span.text
            
    out_lot['auction_house'] = [p.text for p in pars[5:]]
     # [name, data, location]
    return out_lot

def filter_data_art_piece_short(lots):
    import re
    filtered_lots = []
    for lot in lots:
        filtered_lot = parse_short_lot(lot)
        filtered_lots.append(filtered_lot.copy())
        print '{} of {}: '.format(len(filtered_lots), len(lots), filtered_lot['title'])
    return filtered_lots

    
def write_to_csv(art_piece_data, filename='test_output.xlsx'):
    # take the parsed HTML for a given dictionary of data 
    # and generate a CSV file
    df = pd.DataFrame()
    
    for artist_path, lots in art_piece_data.iteritems():
        tmp_df = pd.DataFrame(lots)
        df = df.append(tmp_df)
    
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    df.to_excel(writer, index=False)
    writer.save()
                

def get_all_artists_data(artists, driver, fname):
    for k, v in artists.iteritems():
        # get the art piece information in listings per artist
        get_artist_data_short(k, driver, fname)
        
    
def check_all_artist_paths(artists, driver):
    for sub_path in list(artists.keys()):
        go_to_artist(sub_path, driver)

          
def main():
    driver = login()
   # check_all_artist_paths(artists, driver)
    get_all_artists_data(artists, driver, FILENAME)


def test_filter_data_art_piece():
    #Write data out to file
    pkl_file = open(FILENAME, 'rb')
    out_data = pickle.load(pkl_file)
    
    filter_data_art_piece(out_data)
    
def test_get_artist_data_short():
    driver = login()
    test_filename = 'data_test_a.pickle'
    test_artist_path = "/artist/135880/carlos-rojas/"
    with open(test_filename, 'wb') as pkl_file:
        pickle.dump(artists, pkl_file)
    get_artist_data_short(test_artist_path, driver, test_filename)
    return driver
    


def test_read_artist_data_short():
    test_filename = FILENAME
    test_artist_path = "/artist/144730/beatriz-gonzalez/"
    with open(test_filename, 'rb') as f:
        data = pickle.load(f)
        data[test_artist_path]
    
    # now try to parse the data from beautiful soup
    read_data = data[test_artist_path]
    print read_data[0]
    return read_data

def test_parse_short_lot():
    data = test_read_artist_data_short()
    lot = parse_short_lot(data[0])
    print lot
    return lot

def test_filter_data():
    test_filename = FILENAME
    out_filename = OUTFILENAME
    with open(test_filename, 'rb') as f:
        data = pickle.load(f)
    
    filtered_data = artists
    for artist, lots in data.iteritems():
        print artist
        filtered_data[artist] = filter_data_art_piece_short(lots)
    
    write_to_csv(filtered_data, out_filename)
    return filtered_data
    

if __name__ == '__main__':
    import os
    os.chdir(r'C:\Users\rgaviria\Projects\sandbox')
    # main()
    # test_filter_data_art_piece()
    # test_parse_short_lot()
    # test_get_artist_data_short()
    d = test_filter_data()
    