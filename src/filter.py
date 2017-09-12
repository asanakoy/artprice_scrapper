from bs4 import BeautifulSoup
from src.config import config
import sys
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
def parse_short_lot(lot):
    out_lot = config['TEMPLATE_LOT']
    soup = BeautifulSoup(lot, 'lxml')
    divs = soup.div.find_all('div')

    # Get the data into structure
    out_lot['lot'] = divs[0].p.text
    # relative path to the lot for more info
    out_lot['address'] = str(divs[2].a['href'])
    out_lot['image'] = divs[2].img['src']  # url
    # string Title of the art piece (a {'title'})
    out_lot['title'] = str(soup.find(attrs={'title': True})['title'])

    for div in soup.findAll('div'):
        if div.date:
            main_div = div
            break

    out_lot['date'] = main_div.date.text,  # year drawn

    pars = main_div.find_all('p')
    type_and_size = pars[2]

    # @todo needs to be parsed
    type_par = main_div.find('p', text='cm x')
    #out_lot['type'] = ','.join(type_par.text.split(',')[:-1])  # (str) Painting type
                                                                    # 
    
    out_lot['size'] = main_div.find('span', {'ng-show': "unite_to == 'cm'"}).text  # (zip(int))size in string width x height
    
    size_split = out_lot['size'].split('x')
    if len(size_split) == 2:
        out_lot['width_cm'] = size_split[0].strip('cm')
        out_lot['height_cm'] = size_split[1].strip('cm')

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


def clean_up_short_lot(lot):
    for attr, data in lot.iteritems():
        if type(data) is (unicode or str):
            data = re.sub('[(  )+]', '', data)
            data = re.sub('[\n]+', ' ', data)
            lot[attr] = data
    
    # Custom cleanup
    lot['auction_house'] = ','.join((lot['auction_house']).split(','))
    # @todo remove tuple
    # lot['date'] = lot['date'].encode('ascii', 'replace')
    return lot



def filter_data_art_piece_short(lots):
    import re
    filtered_lots = []
    for lot in lots:
        filtered_lot, lot_divs = parse_short_lot(lot)
        clean_up_short_lot(filtered_lot)
        filtered_lots.append(filtered_lot.copy())
    print '{} of {}: '.format(len(filtered_lots), len(lots), filtered_lot['title'])
    return filtered_lots


def write_to_file(art_piece_data, filename='test_output.xlsx'):
    # take the parsed HTML for a given dictionary of data
    # and generate a CSV file
    df = pd.DataFrame()

    for artist_path, lots in art_piece_data.iteritems():
        tmp_df = pd.DataFrame(lots)
        df = df.append(tmp_df)

    if '.csv' in filename:
        df.to_csv(filename)
    else:
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        df.to_excel(writer, index=False)
        writer.save()
