import os
import pandas as pd
import numpy as np
import pickle
from flask import Flask, request, session, Blueprint, current_app
import json
from models.models import TICK, regist_tick, get_tick_data
from xgboost import XGBRegressor, XGBClassifier
import ta
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from blueprints import v1_1_app


creds = Credentials.from_service_account_file('autotrade-ml-37ca46be841d.json')
service = build('drive', 'v3', credentials=creds)


def classify_buy(x):
    if x > 0.05:
        return 1
    return 0


def classify_sell(x):
    if x < -0.05:
        return 2
    return 0


@v1_1_app.route('/')
def index():
    return 'v1_1'


def ValuePredictor():
    # get tick data from PostgreSQL
    tick_data = get_tick_data()

    data = pd.DataFrame(columns=['time', 'open', 'high', 'low', 'close'])
    for tick_line in tick_data:
        data = data.append({'time': tick_line.time, 'open': tick_line.open, 'high': tick_line.high, 'low': tick_line.low, 'close': tick_line.close}, ignore_index=True)
    data = data.sort_values('time', ascending=True)

    data['open'] = data['open'].astype('float64')
    data['high'] = data['high'].astype('float64')
    data['low'] = data['low'].astype('float64')
    data['close'] = data['close'].astype('float64')

    data['time'] = pd.to_datetime(data['time'], unit='s')

    dataset = data[['open', 'high', 'low', 'close']].copy()

    # sma
    sma5 = ta.trend.SMAIndicator(dataset['close'], 5)
    sma20 = ta.trend.SMAIndicator(dataset['close'], 20)
    dataset['sma5_close'] = sma5.sma_indicator() / dataset['close']
    dataset['sma20_close'] = sma20.sma_indicator() / dataset['close']

    # rsi
    rsi14 = ta.momentum.RSIIndicator(dataset['close'], 14)
    dataset['rsi14_rsi'] = rsi14.rsi()

    # macd
    macd = ta.trend.MACD(dataset['close'])
    dataset['macd_macd'] = macd.macd()

    # bollinger bands
    bband = ta.volatility.BollingerBands(dataset['close'])
    dataset['bband_+2a'] = bband.bollinger_hband() / dataset['close']
    dataset['bband_-2z'] = bband.bollinger_lband() / dataset['close']

    to_predict = dataset.dropna()[-1:]
    xgb_model = XGBClassifier()
    # xgb_model.load_model('model_v2.json')
    xgb_model.load_model(service.files().get_media(fileId='13YzX7BqPTWDAbNooi3SPJsY9EUFguJVT').execute())
    # gbm_buy = pickle.load(open('model_v2.pkl','rb'))
    result = xgb_model.predict(to_predict)

    return str(result[-1])


@v1_1_app.route('/predict',methods=['POST'])
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
