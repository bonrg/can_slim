import logging.config
import os
from pathlib import Path
from collections import namedtuple

DEBUG = True if os.environ.setdefault('DEBUG', '').lower() == 'true' else False
BASE_DIR = 'src'
ABS_BASE_DIR = str([p for p in Path(__file__).absolute().parents if p.name == BASE_DIR][0])
IMG_DIR = f'{ABS_BASE_DIR}/img'


# Logging
# ----------------------------------------------------------------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {'main': {'format': '[%(levelname)s] [%(asctime)s] [%(module)s:%(lineno)d] [V1] %(message)s',
                            'datefmt': '%d/%m/%Y %H:%M:%S'}},
    'handlers': {
        'console': {'level': 'DEBUG', 'class': 'logging.StreamHandler', 'formatter': 'main'},
    },
    'loggers': {
        'RabbitConsumer': {'handlers': ['console'], 'propagate': False, 'level': 'INFO'},
        'RabbitPublisher': {'handlers': ['console'], 'propagate': False, 'level': 'INFO'},
        'main': {'handlers': ['console'], 'propagate': False, 'level': 'INFO'},
    }
}
logging.config.dictConfig(LOGGING)
# ----------------------------------------------------------------------------------------------------------------------
TICKER_URL = 'https://www.nyse.com/api/quotes/filter'
EPS_URL = 'https://ycharts.com/companies/'
ROE_URL = 'https://www.macrotrends.net/stocks/charts/'
ROE_TICKER_URL = 'https://www.macrotrends.net/assets/php/ticker_search_list.php?_=1585413925067'

HEADER = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Ubuntu Chromium/80.0.3987.87 Chrome/80.0.3987.87 Safari/537.36'}
TIMEOUT = 10