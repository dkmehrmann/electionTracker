import pandas as pd
import requests
import re
import ast


# fte
def get_fte():
    '''get the fivethirtyeight primary forecast'''

    r = requests.get(f'https://projects.fivethirtyeight.com/2020-election-forecast/us_timeseries.json')
    res = {
        'candidate': [],
        'date': [],
        'winprob': []
    }

    for candidate in r.json()[0]['candidates']:
        cname = candidate['candidate']
        for date in candidate['dates']:
            res['candidate'].append(cname)
            res['date'].append(date['date'])
            res['winprob'].append(date['winprob'])

    df = pd.DataFrame(res)
    df['date'] = pd.to_datetime(df['date'])
    df['source'] = '538'
    return df


# gjp
def get_gjp():

    r = requests.get("https://goodjudgment.io/superforecasts/")
    l = ast.literal_eval(re.search("data1338.addRows\(\[(.*)\]\);", r.text).group(1).strip())
    df = pd.DataFrame(l)
    df.columns = ['date', 'Biden', 'Trump', 'Other']
    df = pd.melt(df, id_vars='date', var_name='candidate', value_name='winprob')
    df['date'] += ' 2020'
    df['date'] = pd.to_datetime(df['date'])
    df['source'] = 'GJP'
    return df


# predictit
def get_predictit(market_id=3698):
    '''get historical predictit data'''

    df = pd.read_json(
        f'https://www.predictit.org/api/Public/GetMarketChartData/{market_id}?timespan=90d&maxContracts=6&showHidden=true')
    df = df.rename(columns={'contractName': 'candidate'})
    df['winprob'] = df['closeSharePrice'] * 100
    df = df[['candidate', 'date', 'winprob']]
    df['source'] = 'predictit'
    df['date'] = pd.to_datetime(df['date'])

    return df


def get_data():

    df = pd.concat([
        get_fte(),
        get_gjp(),
        get_predictit()
    ])
    df = df[df.date >= df[df.source == 'predictit'].date.min()]

    return df[df.candidate == 'Biden'].pivot('date', 'source', 'winprob').reset_index()

def get_chart_data():
    chartData = {}
    df = get_data().dropna()
    df['date'] = df['date'].astype(str)
    for m in df.columns:
        if m != 'date':
            chartData[m] = df[['date', m]].rename(columns={'date': 'x', m: 'y'}).to_dict('records')
    return chartData