import os
import pandas as pd
import numpy as np
import pickle
from flask import Flask, request, session, Blueprint, current_app
import json
from models.models import TICK, regist_tick, get_tick_data
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from blueprints import v1_app


creds = Credentials.from_service_account_file('autotrade-ml-37ca46be841d.json')
service = build('drive', 'v3', credentials=creds)


@v1_app.route('/')
def index():
    return 'v1'


def ValuePredictor():
    # get tick data from PostgreSQL
    tick_data = get_tick_data()

    # access to predict model in the Google Drive
    gbm_buy = pickle.loads(service.files().get_media(fileId='1nWNZspSDTy_xHrulLzWEIetyRZpIFGW7').execute())
    gbm_sell = pickle.loads(service.files().get_media(fileId='1GAHwj8Zn1gYxxmiUiJWvkSosUULqqKA3').execute())

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
    dataset['y'] = data['high'].shift(-1)

    for i in range(1, 13):
        dataset['shift%s'%i] = data['high'].shift(i)

    dataset['sma5'] = data['high'].rolling(5).mean()
    dataset['sma15'] = data['high'].rolling(15).mean()

    dataset = dataset[100:-1]

    to_predict = dataset[-1:].drop('y', axis=1)
    # gbm_buy = pickle.load(open('model.pkl','rb'))
    result_buy = gbm_buy.predict(to_predict)

    # for Selling trade
    dataset = data[['open', 'high', 'low', 'close', 'day', 'month', 'year', 'day_of_week', 'day_of_year', 'hour', 'minute']].copy()
    dataset['y'] = data['low'].shift(-1)

    for i in range(1, 13):
        dataset['shift%s'%i] = data['low'].shift(i)

    dataset['sma5'] = data['low'].rolling(5).mean()
    dataset['sma10'] = data['low'].rolling(10).mean()
    dataset['sma15'] = data['low'].rolling(15).mean()

    dataset = dataset[100:-1]

    to_predict = dataset[-1:].drop('y', axis=1)
    # gbm_sell = pickle.load(open('model_sell.pkl','rb'))
    result_sell = gbm_sell.predict(to_predict)

    return str(result_buy[0]) + "," + str(result_sell[0])


@v1_app.route('/predict',methods=['POST'])
def v1_predict():
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
