import requests
import config
import pandas as pd
import re

from logging import getLogger
from pyquery import PyQuery as pq
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

logger = getLogger('main')


def get_html_eps(ticker: str) -> str:
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
    values = list(args)
    max_val = max(values)
    values.remove(max_val)
    if val1 > val2 > 0:
        ratio = ((max_val - values[0]) / val2) * 100
    elif max_val < 0:
        ratio = ((max_val - values[0]) / val2) * 100
    else:
        ratio = - ((max_val - values[0]) / val2) * 100
    # ratio = ((val1 - val2) / val2) * 100
    return f'{ratio:.1f}'


def form_chart_quarter_eps(ticker: str, eps_data: dict):
    """Forming chart from last year quarter eps values"""
    last_year = list(eps_data.keys())[0].split('-')[0]
    data_frame = {key: value for (key, value) in eps_data.items() if last_year in key}
    fig1, ax1 = plt.subplots()
    plt.xlabel('Quarter')
    plt.ylabel('EPS')
    plt.title(f'Quarterly EPS indicator - {ticker.upper()}')
    ax1.bar(*zip(*data_frame.items()))
    fig1.savefig(f'{config.IMG_DIR}/{ticker}_q_eps')
    plt.close(fig1)


def get_annual_eps_value(eps_data: dict):
    """calculate annual EPS values"""
    years = list(set([int(k.split('-')[0]) for (k, v) in eps_data.items()]))
    max_year = max(years)
    three_years_ago = max_year - 3
    filter_years = sorted([str(x) for x in years if max_year >= x >= three_years_ago], reverse=True)
    values = list()
    for year in filter_years:
        values.append(round(sum([v for (k, v) in eps_data.items() if year in k]), 2))
    return dict(zip(filter_years, values))


def get_annual_percentage_ratio(**kwargs):
    keys = list(kwargs.keys())[0:-1]
    values = list(kwargs.values())
    pair_values = tuple(zip(values[::1], values[1::1]))
    percentage_ratio = [f'{get_percantage_ratio(*v)}%' for v in pair_values]
    return dict(zip(keys, percentage_ratio))


def form_chart_annual_eps(ticker: str, eps_data_annual: dict):
    """Forming chart sum of annual eps values"""
    fig2, ax2 = plt.subplots()
    plt.xlabel('Years')
    plt.ylabel('EPS')
    plt.title(f'Annually EPS indicator - {ticker.upper()}')
    ax2.bar(*zip(*eps_data_annual.items()))
    fig2.savefig(f'{config.IMG_DIR}/{ticker}_a_eps')
    plt.close(fig2)


def check_ticker_nyse(ticker: str) -> dict:
    try:
        json = {"normalizedTicker": ticker.upper()}
        request = requests.post(config.NYSE_TICKER_URL, json=json, timeout=config.TIMEOUT)
        if request.status_code == 200:
            return request.json()
    except Exception as e:
        logger.warning(e)


def check_ticker_nasdaq(ticker: str) -> dict:
    try:
        request = requests.get(f'{config.NASDAQ_TICKER_URL}{ticker.upper()}/info?assetclass=stocks',
                               timeout=config.TIMEOUT)
        if request.status_code == 200 and request.json().get('status').get('rCode') == 200:
            return request.json()
    except Exception as e:
        logger.warning(e)

def get_url_param_for_roe(ticker: str) -> str:
    try:
        request = requests.get(config.ROE_TICKER_URL, headers=config.HEADER, timeout=config.TIMEOUT)
        if request.status_code == 200:
            param = re.search(r'{0}\\/\w+'.format(ticker), request.text).group(0)
            return re.sub(r'\\', '', param)
    except Exception as e:
        logger.warning(e)


def get_html_roe(param: str):
    try:
        request = requests.get(f'{config.ROE_URL}{param}/roe')
        if request.status_code == 200:
            return request.text
    except Exception as e:
        logger.warning(e)


def get_roe_data(content: str):
    html = pq(content)
    table = html('table[class^="table"]').eq(0)
    tbody= table('tbody')
    td_date = tbody('td:nth-of-type(1)')
    td_value = tbody('td:nth-of-type(4)')
    dates = [td.text for td in td_date]
    values = [td.text for td in td_value]
    return dict(zip(dates, values))


def get_roe_three_year_data(roe_data: dict):
    last_quarter = list(roe_data.keys())[0]
    last_quarter_date = datetime.strptime(last_quarter, '%Y-%m-%d').date()
    dates = [str(last_quarter_date)]
    for i in range(3):
        years_ago_quarter_date = last_quarter_date - timedelta(days=365)
        last_quarter_date = years_ago_quarter_date
        dates.append(str(years_ago_quarter_date))
    data = {k: v for (k, v) in roe_data.items() if k in dates}
    data = {k.split('-')[0]: float(re.sub(r'%', '', v)) for (k, v) in data.items()}
    return data


def form_chart_annual_roe(ticker: str, roe_data: dict):
    """Forming chart annually roe percentage data"""
    fig3, ax3 = plt.subplots()
    plt.xlabel('Years')
    plt.ylabel('ROE percentage (%)')
    plt.title('Annually ROE indicator')
    ax3.bar(*zip(*roe_data.items()))
    fig3.savefig(f'{config.IMG_DIR}/{ticker}_a_roe')
    plt.close(fig3)


if __name__ == '__main__':
    ticker = "ATVI"
    info = check_ticker_nasdaq(ticker)
    print(info)
    # html = get_html_eps(ticker)
    # eps = get_eps_data(html)
    # eps_annual = get_annual_eps_value(eps)
    # per = get_annual_percentage_ratio(**eps_annual)
    # form_chart_annual_eps(ticker, eps_annual)
    # form_chart_quarter_eps(ticker, eps)
    # print(eps_annual)
    # print(per)
    # form_chart_annual_eps(ticker, eps_annual)
    # form_chart_quarter_eps(ticker, eps)

    # param = get_url_param_for_roe(ticker)
    # html = get_html_roe(param)
    # roe = get_roe_data(html)
    # data = get_roe_three_year_data(roe)
    # form_chart_annual_roe(ticker, data)

