import os.path as path
from secrets import secrets
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
          'auction_house': [],  # [name, location]
          'width_cm': None,
          'height_cm': None,
          'depth_cm': None,
          'auction_date': None,
          'auction_date_day': None,
          'auction_date_month': None,
          'auction_date_year': None,
          'category': None,
          'medium': None
         },

  'BASE_URL': "https://www.artprice.com/",
  'FILENAME': 'data_full_test.pickle',
  'OUTFILENAME': 'data_output.xlsx',
  'CSV_FILENAME': 'output.csv',
  'DATA_PATH': path.join(path.dirname(path.realpath(__file__)), r'../data'),
  'SECRETS': secrets
}
