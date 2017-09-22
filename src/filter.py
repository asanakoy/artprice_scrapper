from bs4 import BeautifulSoup
from src.config import config
import sys
import urlparse
import pickle
reload(sys)
sys.setdefaultencoding('utf8')
import pandas as pd
import re

##
## @brief      Parses stored HTML/XML from pickled file
##
## @param      lot   a specific art lot (HTML) content
##
## @return     lot   in the format specified by 'TEMPLATE_LOT' in configuration
## @return     divs  the divs found by BeautifulSoup on the lot for debugging purposes
##
def parse(lot):
    out_lot = config['TEMPLATE_LOT']
    soup = BeautifulSoup(lot, 'lxml')
    divs = soup.div.find_all('div')

    out_lot['lot'] = divs[0].p.text
    # relative path to the lot for more info
    out_lot['address'] = urlparse.urljoin(config['BASE_URL'], str(divs[2].a['href']))
    out_lot['image'] = divs[2].img['src']  # url
    # string Title of the art piece (a {'title'})
    out_lot['title'] = str(soup.find(attrs={'title': True})['title'])

    for div in soup.findAll('div'):
        if div.date:
            main_div = div
            break

    out_lot['date'] = ''.join(main_div.find('date').text.encode('ascii', 'ignore'))  # year drawn
    out_lot['date'] = out_lot['date']
    out_lot['date'] = main_div.find('date').text
    pars = main_div.find_all('p')
    # @todo needs to be parsed
    type_par = pars[2]

    size_cm_el = main_div.find('span', {'ng-show': "unite_to == 'cm'"})  # (zip(int))size in string width x height
    size_in_el = main_div.find('span', {'ng-show': "unite_to == 'in'"})

    size_cm_text = size_cm_el.text
    size_in_text = size_in_el.text

    out_lot['size'] = size_cm_text

    type_text = type_par.text
    type_text = re.sub(size_in_text, '', type_text)
    type_text = re.sub(size_cm_text, '', type_text)
    out_lot['type'] =  type_text
    out_lot['category'] = type_text.split(',')[0]
    out_lot['medium']= ','.join(type_text.split(',')[1:])

    size_split = out_lot['size'].split('x')
    if len(size_split) == 2:
        out_lot['width_cm'] = size_split[0]
        out_lot['height_cm'] = size_split[1]
        out_lot['depth_cm'] = size_split[2] if len(size_split) > 2 else ''

    # get price estimats
    for span in pars[3].find_all('span', {'ng-show': True}):
        if 'USD' in span['ng-show']:
            out_lot['estimate_price'] = span.text

    # get hammer price
    for span in pars[4].find_all('span', {'ng-show': True}):
        if 'USD' in span['ng-show']:
            out_lot['hammer_price'] = span.text

    # @todo need to find a more effective way of parsing this data
    #       Maybe look into using siblings to find the data I need?
    #       https://stackoverflow.com/questions/34295451/find-elements-which-have-a-specific-child-with-beautifulsoup
    out_lot['auction_house'] = ','.join((p.text for p in pars[-2:]))
    # End of structuring data

    # [name, data, location]
    return out_lot, divs

##
## @brief      Cleans up the structured data and removes duplicates,
##             whitespaces and converts unicode to ascii
##
## @param      lot   The lot already in the dictionary structure 
##                   as expected
##
## @return     the resulting filtered lot
##
def filter(lot):
    for attr, data in lot.iteritems():
        if type(data) is (unicode or str):
            data = re.sub('  +', '', data)
            data = re.sub('[\n]+', '', data)
            data = data.encode('ascii', 'ignore')
            lot[attr] = data

    date_pat = '(\d{2} \D{3} \d{4})(,)'
    date_re = re.compile(date_pat)
    # Custom cleanup
    # convert from unicode to string
    lot['auction_house'] = lot['auction_house']
    auction_date = date_re.findall(lot['auction_house'])
    if not auction_date:
        auction_date = ''
    else:
        auction_date  = auction_date[0][0]
    year = re.findall('\d{4}', lot['date'])
    if year:
        lot['date'] = year[0]
    lot['auction_date'] = auction_date
    lot['auction_house'] = ','.join((lot['auction_house']).split(','))
    lot['auction_house'] = re.sub(date_pat, '', lot['auction_house'])
    lot['width_cm'] = lot['width_cm'].strip(' cm')
    lot['height_cm'] = lot['height_cm'].strip(' cm')
    lot['hammer_price'] = lot['hammer_price'].strip('$ ')
    # Get the day month and year as separate columns
    auction_date_list = auction_date.split(' ')
    lot['auction_date_day'] = auction_date_list[0]
    lot['auction_date_month'] = auction_date_list[1]
    lot['auction_date_year'] = auction_date_list[2]

    # remove spaces
    lot['title'] = lot['title'].replace(' ', '_')

    # @todo remove tuple
    # lot['date'] = lot['date'].encode('ascii', 'replace')
    return lot

##
## @brief      Parses a list containg the scrapped HTML data containing the 
##             lot information
##
## @param      lots  The lots
##
## @return     { description_of_the_return_value }
##
def parse_lots(lots):
    import re
    filtered_lots = []
    for lot in lots:
        filtered_lot, lot_divs = parse(lot)
        filtered_lot = filter(filtered_lot)
        filtered_lots.append(filtered_lot.copy())
    print '{} of {}: '.format(len(filtered_lots), len(lots), filtered_lot['title'])
    return filtered_lots


##
## @brief      Writes the parsed and filtered data to CSV or XLSX file
##
## @param      art_piece_data  The art piece data
## @param      filename        The filename
##
## @return     { description_of_the_return_value }
##
def write_to_file(art_piece_data, filename='test_output.xlsx'):
    # take the parsed HTML for a given dictionary of data
    # and generate a CSV file
    df = pd.DataFrame()

    for artist_path, lots in art_piece_data.iteritems():
        tmp_df = pd.DataFrame(lots)
        tmp_df['artist'] = pd.Series([artist_path for x in range(0,len(tmp_df['auction_house']))])
        df = df.append(tmp_df)
    columns_ordered = ['artist','lot','title','auction_date','date','type', 'category', 'medium','size','hammer_price','auction_house','width_cm','height_cm','depth_cm','auction_date_day','auction_date_month','auction_date_year','address','image','estimate_price']
    df = df.reindex(columns=columns_ordered)
    
    if '.csv' in filename:
        df.to_csv(filename)
    else:
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        df.to_excel(writer, index=False)
        writer.save()


def main():
    with open(config['FILENAME']) as f:
        data = pickle.load(f)
    filtered_data = {}
    for artist, lots in data.iteritems():
        print artist
        filtered_data[artist] = parse_lots(lots)

    write_to_file(filtered_data, config['OUTFILENAME'])

if __name__ == '__main__':
    import os
    os.chdir(config['DATA_PATH'])
    main()