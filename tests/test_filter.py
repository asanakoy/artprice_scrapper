import os
os.sys.path.append(r'c:\Users\rgaviria\Projects\sandbox\artprice_scrapper')
import src.filter as fil
from src.config import config
import pickle
import pprint
import os

# configuration
TEST_FILENAME = os.path.join(config['DATA_PATH'], config['FILENAME'])
TEST_ARTIST_PATH = "/artist/144730/beatriz-gonzalez/"

##
## @brief      Reads raw parsed data from a pickle file and filters the 
##             content and writes to CSV
##
## @return     The filtered data
##
def test_filter_data():
    TEST_FILENAME = os.path.join(config['DATA_PATH'], config['FILENAME'])
    OUT_FILENAME = os.path.join(config['DATA_PATH'], config['OUTFILENAME'])
    with open(TEST_FILENAME, 'rb') as f:
        data = pickle.load(f)

    filtered_data = config['artists']
    for artist, lots in data.iteritems():
        print artist
        filtered_data[artist] = fil.filter_data_art_piece_short(lots)

    fil.write_to_file(filtered_data, 'output.xlsx')
    return filtered_data


def test_read_artist_data_short():
    with open(TEST_FILENAME, 'rb') as f:
        data = pickle.load(f)

    # now try to parse the data from beautiful soup
    read_data = data[TEST_ARTIST_PATH]
    return read_data 


##
## @brief      Tests filter_data_art_piece_short function
##  
## @return     filtered data 
##
def test_parse_data_art_piece_short():
    artist_data = test_read_artist_data_short()
    filtered_data = fil.filter_data_art_piece_short(artist_data[:10])
    
    test_output_data = config['artists']
    test_output_data[TEST_ARTIST_PATH] = filtered_data

    fil.write_to_file(test_output_data, 'test_output.xlsx')
    # pprint.pprint(filtered_data)
    
    return filtered_data

def test_parse_short_lot():
    artist_data = test_read_artist_data_short()
    filtered_lots = []
    divs = []
    for lot in artist_data[:10]:
        filtered_lot, lot_divs = fil.parse_short_lot(lot)
        fil.clean_up_short_lot(filtered_lot)
        filtered_lots.append(filtered_lot)
        divs.append(lot_divs)
        
    pprint.pprint(filtered_lots)
#     for k,v in filtered_lots[0].iteritems():
#         print '{} ({}): {}'.format(k, type(v), v)
    return filtered_lots, divs

if __name__ == '__main__':

    # test_filter_data()
    test_parse_data_art_piece_short()
    # test_parse_short_lot()
