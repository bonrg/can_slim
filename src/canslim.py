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
    return f'{ratio:.1f}'


def form_chart_quarter_eps(ticker: str, eps_data: dict):
    """Forming chart from last year quarter eps values"""
    last_year = list(eps_data.keys())[0].split('-')[0]
    data_frame = {key: value for (key, value) in eps_data.items() if last_year in key}
    fig1, ax1 = plt.subplots()
    ax1.bar(*zip(*data_frame.items()))
    fig1.savefig(f'{config.IMG_DIR}/{ticker}_q_eps')
    plt.close(fig1)


def get_annual_eps_value(eps_data: dict):
    """calculate annual EPS values"""
    last_year = int(list(eps_data.keys())[0].split('-')[0])
    year_1 = str(last_year - 1)
    year_2 = str(last_year - 2)
    year_3 = str(last_year - 3)
    eps_sum_last_year = sum([v for (k, v) in eps_data.items() if str(last_year) in k])
    eps_sum_year_1 = sum([v for (k, v) in eps_data.items() if year_1 in k])
    eps_sum_year_2 = sum([v for (k, v) in eps_data.items() if year_2 in k])
    eps_sum_year_3 = sum([v for (k, v) in eps_data.items() if year_3 in k])
    years = [str(last_year), year_1, year_2, year_3]
    values = [eps_sum_last_year, eps_sum_year_1, eps_sum_year_2, eps_sum_year_3]
    return dict(zip(years, values))


def get_annual_percentage_ratio(**kwargs):
    keys = list(kwargs.keys())[0:-1]
    values = list(kwargs.values())
    pair_values = tuple(zip(values[::1], values[1::1]))
    percentage_ratio = [f'{get_percantage_ratio(*v)}%' for v in pair_values]
    return dict(zip(keys, percentage_ratio))


def form_chart_annual_eps(ticker: str, eps_data_annual: dict):
    """Forming chart sum of annual eps values"""
    fig2, ax2 = plt.subplots()
    ax2.bar(*zip(*eps_data_annual.items()))
    fig2.savefig(f'{config.IMG_DIR}/{ticker}_a_eps')
    plt.close(fig2)


def check_ticker(ticker: str) -> dict:
    try:
        json = {"normalizedTicker": ticker.upper()}
        request = requests.post(config.TICKER_URL, json=json, timeout=config.TIMEOUT)
        if request.status_code == 200:
            return request.json()
    except Exception as e:
        logger.warning(e)


if __name__ == '__main__':
    ticker = "MSFT"
    t = check_ticker(ticker)
    print(t)



