import os
import pandas as pd
import numpy as np
import pickle
from flask import Flask, request, session, Blueprint, current_app
import json
from models.models import TICK, regist_tick, get_tick_data
import ta
from blueprints import v1_3_app
from pycaret.classification import *


@v1_3_app.route('/')
def index():
    return 'v1_3'


def ValuePredictor(item):

    print(item[0])

    train_H1 = pd.DataFrame(item)
    train_H1['SMA20'] = ta.trend.SMAIndicator(train_H1['close'], 20).sma_indicator()
    train_H1['SMA50'] = ta.trend.SMAIndicator(train_H1['close'], 50).sma_indicator()
    train_H1['SMA100'] = ta.trend.SMAIndicator(train_H1['close'], 100).sma_indicator()

    train_H1['h1_open'] = train_H1['open'].shift(11)
    train_H1['h1_high'] = train_H1['high'].rolling(12).max()
    train_H1['h1_low'] = train_H1['low'].rolling(12).min()

    # extract features from date
    train_H1['time'] = pd.to_datetime(train_H1['time'])
    train_H1['day'] = [i.day for i in train_H1['time']]
    train_H1['month'] = [i.month for i in train_H1['time']]
    train_H1['year'] = [i.year for i in train_H1['time']]
    train_H1['day_of_week'] = [i.dayofweek for i in train_H1['time']]
    train_H1['day_of_year'] = [i.dayofyear for i in train_H1['time']]

    train_H1 = train_H1.dropna().reset_index(drop=True)

    print('--------------------------------')
    print(train_H1)
    print('--------------------------------')
    # for Buying trade
    # load the model
    loaded_model = load_model('models/model_v5')
    result_buy = predict_model(loaded_model, data=train_H1)
    print(result_buy)

    return 'test'


@v1_3_app.route('/predict',methods=['POST'])
def predict():
    if request.method == 'POST':
        item = []
        item = request.json['data']
        # print(item['data'][0])

        result_predict = ValuePredictor(item)
        # result_predict = 'test'
        return result_predict
