import src.filter as fil
from src.config import config
import pickle
##
## @brief      Reads raw parsed data from a pickle file and filters the 
##             content and writes to CSV
##
## @return     The filtered data
##
def test_filter_data():
    test_filename = config['FILENAME']
    out_filename = config['OUTFILENAME']
    with open(test_filename, 'rb') as f:
        data = pickle.load(f)

    filtered_data = config['artists']
    for artist, lots in data.iteritems():
        print artist
        filtered_data[artist] = fil.filter_data_art_piece_short(lots)

    fil.write_to_csv(filtered_data, out_filename)
    return filtered_data


if __name__ == '__main__':
    import os
    os.chdir('/Users/RicardoGaviria/Projects/artprice_scrapper/data')

    test_filter_data()