from bs4 import BeautifulSoup
from src.config import config
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import pandas as pd

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
    type_and_size = pars[1].text

    # @todo needs to be parsed
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
    # End of structuring data

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
