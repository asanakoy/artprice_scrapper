import src.filter as fil
from src.config import config
import pickle
import pprint

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

    fil.write_to_file(filtered_data, 'output.csv')
    return filtered_data


def test_read_artist_data_short():
    test_filename = config['FILENAME']
    test_artist_path = "/artist/144730/beatriz-gonzalez/"
    with open(test_filename, 'rb') as f:
        data = pickle.load(f)
        data[test_artist_path]

    # now try to parse the data from beautiful soup
    read_data = data[test_artist_path]
    return read_data 


def test_parse_short_lot():
    test_artist_path = "/artist/144730/beatriz-gonzalez/"
    artist_data = test_read_artist_data_short()
    filtered_data = fil.filter_data_art_piece_short(artist_data[:10])
    
    test_output_data = config['artists']
    test_output_data[test_artist_path] = filtered_data

    pprint.pprint(filtered_data)
    
    return filtered_data

if __name__ == '__main__':
    import os
    os.chdir('/Users/RicardoGaviria/Projects/artprice_scrapper/data')

    # test_filter_data()
    test_parse_short_lot()