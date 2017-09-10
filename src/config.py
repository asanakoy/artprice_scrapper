config = {
  # Constant variables
  'artists': {
      "/artist/144730/beatriz-gonzalez/": [],
      "/artist/140609/jorge-cavelier/": [],
      "/artist/135880/carlos-rojas/": [],
      "/artist/21426/alejandro-obregon/": [],
      "/artist/23813/eduardo-ramirez-villamizar/": [],
      "/artist/23957/omar-rayo/": [],
      "/artist/20967/edgar-negret/": [],
      "/artist/145472/doris-salcedo/": [],
      "/artist/3363/fernando-botero/": [],
      "/artist/36340/margarita-lozano/": []
  },
  'TEMPLATE_LOT': {
         'lot': None,  # int
         'address': None,  # relative path to the lot for more info
         'image': None,  # url
         'title': None,  # string Title of the art piece (a {'title'})
         'date': None,  # year drawn
         'type': None,  # (str) Painting type
         'size': None,  # (zip(int))size in string width x height
         'estimate_price': None,  # (lower, upper) price in USD
         'hammer_price': None,  # int
         'auction_house': []  # [name, location]
         },

  'BASE_URL': "https://www.artprice.com/",
  'FILENAME': 'data_full_test.pickle',
  'OUTFILENAME': 'data_output.xlsx',
  'CSV_FILENAME': 'output.csv'
}
