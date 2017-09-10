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
    lot = art_s.parse_short_lot(data[0])
    print lot
    return lot

if __name__ == '__main__':
    import os
    os.chdir('/Users/RicardoGaviria/Projects/artprice_scrapper/data')
    # test_filter_data_art_piece()
    # test_parse_short_lot()
    # test_get_artist_data_short()
    d = test_filter_data()