import os
from .context import src
import pickle
import pprint
import os


##
## Global variables
##
TEST_FILENAME = os.path.join(src.config['DATA_PATH'], src.config['FILENAME'])
OUT_FILENAME = os.path.join(src.config['DATA_PATH'], src.config['OUTFILENAME'])
TEST_ARTIST_PATH = "/artist/144730/beatriz-gonzalez/"

def sample_parsed_data():
    parsed = {
            'address': '/artist/144730/beatriz-gonzalez/print-multiple/13963536/sin-titulo',
            'auction_house': u'\n\n              Bogota Auctions\n          \n          ,\n          15 Aug 2017\n\n      ,\n          Colombia\n        ',
            'date': u'\n            (1992)\n          ',
            'estimate_price': u'\n              $ 170 - $ 238\n                  ',
            'hammer_price': u'\n              Lot not sold\n                 ',
            'height_cm': u' 29.5 cm',
            'image': 'https://imgprivate2.artprice.com/lot/MTExNzYwODg5NjgxOTQwNTIyLQ==/NTIxMzgwOTc5NDM2NDM5OTA4NzQ4MDMwODI3LQ==/sml/1',
            'lot': u'\n        Lot #\n          38\n      ',
            'size': u'20 cm x 29.5 cm',
            'title': 'Sin t\xc3\xadtulo',
            'type': None,
            'width_cm': u'20 cm '}

    filtered = {'address': 'https://www.artprice.com/artist/144730/beatriz-gonzalez/print-multiple/13963536/sin-titulo',
        'auction_house': 'Bogota Auctions,Colombia',
        'auction_date' : '15 Aug 2017',
        'date': ('1992'),
        'estimate_price': '$ 170 - $ 238',
        'hammer_price': 'Lot not sold',
        'height_cm': '29.5',
        'image': 'https://imgprivate2.artprice.com/lot/MTExNzYwODg5NjgxOTQwNTIyLQ==/NTIxMzgwOTc5NDM2NDM5OTA4NzQ4MDMwODI3LQ==/sml/1',
        'lot': 'Lot #38',
        'size': '20 cm x 29.5 cm',
        'title': 'Sin t\xc3\xadtulo',
        'type': 'Print-Multiple,Silkscreen,',
        'width_cm': '20'}

    ##
    ## Prepare this data by calling the function defined below
    ##
    ##
    def prepare_parsed():
        artist_data = prepare_input()
        parsed_lot, lot_divs = src.filter.parse(artist_data[0])
        return parsed_lot

    parsed = prepare_parsed()
    pprint.pprint(parsed)
    return parsed, filtered

##
## @brief      Gets the test data to use as inputs to most of these tests
##
## @return     { description_of_the_return_value }
##
def prepare_input():
    with open(TEST_FILENAME, 'rb') as f:
        data = pickle.load(f)

    # now try to parse the data from beautiful soup
    read_data = data[TEST_ARTIST_PATH]
    return read_data 


##
## @brief      Reads raw parsed data from a pickle file and filters the 
##             content and writes to CSV
##
## @return     The filtered data
##
def test_parse_artists_data():
    with open(TEST_FILENAME, 'rb') as f:
        data = pickle.load(f)

    filtered_data = src.config['artists']
    for artist, lots in data.iteritems():
        print artist
        filtered_data[artist] = src.filter.parse_lots(lots)

    src.filter.write_to_file(filtered_data, 'output.xlsx')
    return filtered_data


##
## @brief      Tests filter_data_art_piece_short function
##  
## @return     filtered data 
##
def test_parse_lots(num):
    artist_data = prepare_input()
    filtered_data = src.filter.parse_lots(artist_data[:num])
    # test_output_data = src.config['artists']
    # test_output_data[TEST_ARTIST_PATH] = filtered_data

    # src.filter.write_to_file(test_output_data, 'test_output.xlsx')
    
    return filtered_data


def test_parse(num=10):
    artist_data = prepare_input()
    filtered_lots = []
    divs = []
    parsed_lots = []
    for lot in artist_data[:num]:
        parsed_lot, lot_divs = src.filter.parse(lot)
        filtered_lot = src.filter.filter(parsed_lot)
        filtered_lots.append(filtered_lot)
        divs.append(lot_divs)
        parsed_lots.append(parsed_lot)

    # pprint.pprint(filtered_lots)
#     for k,v in filtered_lots[0].iteritems():
#         print '{} ({}): {}'.format(k, type(v), v)
    return filtered_lots, parsed_lots, divs

def test_filter():
    artist_data = prepare_input()
    parsed_data, exp_filtered_data = sample_parsed_data()
    print exp_filtered_data
    filtered_data = src.filter.filter(parsed_data)

    def test_types(test_d, good_d):
        for k, v in test_d.iteritems():
            assert type(good_d[k]) == type(v), 'type Error: {}'.format(k)

    def test_values(test_d, good_d):
        for k, v in test_d.iteritems():
            assert good_d[k] == v, 'value Error: {}'.format(k)

    test_types(filtered_data, exp_filtered_data)
    test_values(filtered_data, exp_filtered_data)

if __name__ == '__main__':
    # configuration
    os.chdir(src.config['DATA_PATH'])
    # test_filter_data()
    # test_parse_lots()
    # test_parse_short_lot()
    test_filter()
