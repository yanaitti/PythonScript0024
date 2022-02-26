import os
import pandas as pd
import numpy as np
import pickle
from flask import Flask, request, session, Blueprint, current_app
from flask_caching import Cache
import json
from models.models import TICK, regist_tick, get_tick_data
import ta
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from blueprints import v1_2_app


creds = Credentials.from_service_account_file('autotrade-ml-37ca46be841d.json')
service = build('drive', 'v3', credentials=creds)


@v1_2_app.route('/')
def index():
    return 'v1_2'


def ValuePredictor():
    # get tick data from PostgreSQL
    tick_data = get_tick_data()

    # access to predict model in the Google Drive
    # gbm_buy = pickle.loads(service.files().get_media(fileId='1lVZNFTmTDCQK-eG19OE5bYRcN3Fg4X8H').execute())
    # gbm_sell = pickle.loads(service.files().get_media(fileId='14eE4-D5g6lqTzvKZJZSccbcXeKYv3Zcc').execute())
    gbm_buy = cache.get('ml_model_v3_buy') if cache.get('ml_model_v3_buy') else pickle.loads(service.files().get_media(fileId='1lVZNFTmTDCQK-eG19OE5bYRcN3Fg4X8H').execute())
    gbm_sell = cache.get('ml_model_v3_sell') if cache.get('ml_model_v3_sell') else pickle.loads(service.files().get_media(fileId='14eE4-D5g6lqTzvKZJZSccbcXeKYv3Zcc').execute())

    data = pd.DataFrame(columns=['time', 'open', 'high', 'low', 'close'])
    for tick_line in tick_data:
        data = data.append({'time': tick_line.time, 'open': tick_line.open, 'high': tick_line.high, 'low': tick_line.low, 'close': tick_line.close}, ignore_index=True)
    data = data.sort_values('time', ascending=True)
    # print(data)

    data['open'] = data['open'].astype('float64')
    data['high'] = data['high'].astype('float64')
    data['low'] = data['low'].astype('float64')
    data['close'] = data['close'].astype('float64')

    data['time'] = pd.to_datetime(data['time'], unit='s')

    # extract features from date
    data['day'] = [i.day for i in data['time']]
    data['month'] = [i.month for i in data['time']]
    data['year'] = [i.year for i in data['time']]
    data['day_of_week'] = [i.dayofweek for i in data['time']]
    data['day_of_year'] = [i.dayofyear for i in data['time']]

    data['hour'] = [i.hour for i in data['time']]
    data['minute'] = [i.minute for i in data['time']]

    # for Buying trade
    dataset = data[['open', 'high', 'low', 'close', 'day', 'month', 'year', 'day_of_week', 'day_of_year', 'hour', 'minute']].copy()

    for i in range(1, 13):
        dataset['shift%s_open'%i] = data['open'].shift(i)
        dataset['shift%s_high'%i] = data['high'].shift(i)
        dataset['shift%s_low'%i] = data['low'].shift(i)
        dataset['shift%s_close'%i] = data['close'].shift(i)

    # sma
    sma5 = ta.trend.SMAIndicator(data['close'], 5)
    sma15 = ta.trend.SMAIndicator(data['close'], 15)
    dataset['sma5_close'] = sma5.sma_indicator() / data['close']
    dataset['sma15_close'] = sma15.sma_indicator() / data['close']

    # rsi
    rsi14 = ta.momentum.RSIIndicator(data['close'], 14)
    dataset['rsi14_rsi'] = rsi14.rsi()

    # macd
    macd = ta.trend.MACD(data['close'])
    dataset['macd_macd'] = macd.macd()

    # bollinger bands
    bband = ta.volatility.BollingerBands(data['close'])
    dataset['bband_+2a'] = bband.bollinger_hband() / data['close']
    dataset['bband_-2z'] = bband.bollinger_lband() / data['close']

    to_predict = dataset.dropna()[-1:]
    # gbm_buy = pickle.load(open('model_v3_buy.pkl','rb'))
    result_buy = gbm_buy.predict(to_predict)

    # for Selling trade
    # gbm_sell = pickle.load(open('model_v3_sell.pkl','rb'))
    result_sell = gbm_sell.predict(to_predict)

    return str(result_buy[0]) + "," + str(result_sell[0])


@v1_2_app.route('/predict',methods=['POST'])
def predict():
    if request.method == 'POST':

        if current_app.config['W_UPDATE'] == 'True':
            curr = []
            curr = TICK.query.filter(TICK.time==request.json['time']).all()
            if(len(curr) == 0):
                items_idx = list()
                item = dict()
                item['currency'] = request.json['curr']
                item['period'] = request.json['perd']
                item['time'] = request.json['time']
                item['open'] = request.json['open']
                item['high'] = request.json['high']
                item['low'] = request.json['low']
                item['close'] = request.json['close']
                items_idx.append(item)

                db.session.execute(TICK.__table__.insert(), items_idx)
                db.session.commit()

        result_predict = ValuePredictor()
        return result_predict
