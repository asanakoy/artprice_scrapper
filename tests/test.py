from src.scrapper import scrapper as art_s

def test_filter_data_art_piece():
    # Write data out to file
    pkl_file = open(FILENAME, 'rb')
    out_data = pickle.load(pkl_file)

    art_s.filter_data_art_piece(out_data)


def test_get_artist_data_short():
    driver = art_s.login()
    test_filename = 'data_test_a.pickle'
    test_artist_path = "/artist/135880/carlos-rojas/"
    with open(test_filename, 'wb') as pkl_file:
        pickle.dump(artists, pkl_file)
    art_s.get_artist_data_short(test_artist_path, driver, test_filename)
    return driver

if __name__ == '__main__':
    import os
    os.chdir('/Users/RicardoGaviria/Projects/artprice_scrapper/data')
    # test_filter_data_art_piece()
    # test_parse_short_lot()
    # test_get_artist_data_short()
    d = test_filter_data()