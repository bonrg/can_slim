import requests
import config
import pandas as pd

from logging import getLogger
from pyquery import PyQuery as pq
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

logger = getLogger('main')


def get_html_text(ticker: str) -> str:
    try:
        if isinstance(ticker, str):
            data = requests.get(f'{config.EPS_URL}{ticker.upper()}/eps', headers=config.HEADER, timeout=config.TIMEOUT)
            if data.status_code == 200:
                return data.text
            elif data.status_code == 404:
                logger.warning('No such ticker')
            else:
                logger.warning('Something wrong')
    except Exception as e:
        logger.warning(e)


def get_eps_data(content: str) -> dict:
    html = pq(content)
    table = html('table.histDataTable')
    td_date = table('td.col1')
    td_value = table('td.col2')
    dates = [str(pd.to_datetime(td.text).date()) for td in td_date]
    values = [float(td.text) for td in td_value]
    eps_data = dict(zip(dates, values))
    return eps_data


def get_quarter_eps_values(eps_data: dict) -> tuple:
    last_quarter = list(eps_data.keys())[0]
    last_quarter_date = datetime.strptime(last_quarter, '%Y-%m-%d').date()
    years_ago_quarter_date = last_quarter_date - timedelta(days=365)
    last_quarter_value = eps_data[last_quarter]
    years_ago_quarter_value = eps_data[str(years_ago_quarter_date)]
    return last_quarter_value, years_ago_quarter_value


def get_percantage_ratio(*args) -> str:
    val1, val2 = args
    ratio = (val1 - val2) / val2 * 100
    return f'{ratio:.1f}%'


def form_chart(ticker: str, eps_data: dict):
    """Forming chart from last year eps values"""
    last_year = list(eps_data.keys())[0].split('-')[0]
    data_frame = {key: value for (key, value) in eps_data.items() if last_year in key}
    plt.bar(*zip(*data_frame.items()))
    plt.savefig(f'{config.IMG_DIR}/{ticker}')




if __name__ == '__main__':
    ticker = "ATVI"
    cont = get_html_text(ticker)
    tabl = get_eps_data(cont)
    val = get_quarter_eps_values(tabl)
    rat = get_percantage_ratio(*val)
    print(rat)
    print(tabl)
    form_chart(ticker, tabl)

