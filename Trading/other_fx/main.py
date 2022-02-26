import os
import pandas as pd
import numpy as np
import flask
import pickle
import psycopg2
from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, asc, desc

app=Flask(__name__)
app.secret_key = 'secret'

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:admin@localhost:5432/postgres')
W_UPDATE = os.environ.get('W_UPDATE', 'T')

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
db = SQLAlchemy(app)

# Database Connection
if os.environ.get('DATABASE_URL') == None:
    conn = psycopg2.connect(DATABASE_URL)
else:
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')


class TICK(db.Model):
    __tablename__ = "t_tick"
    id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.String(), nullable=False)
    period = db.Column(db.String(), nullable=False)
    time = db.Column(db.Integer, nullable=False)
    open = db.Column(db.Numeric, nullable=False)
    high = db.Column(db.Numeric, nullable=False)
    low = db.Column(db.Numeric, nullable=False)
    close = db.Column(db.Numeric, nullable=False)


@app.route('/')
def index():
    return ''


def ValuePredictor():

    tick_data = TICK.query.order_by(desc(TICK.id)).limit(200)
    # print(type(tick_data))

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
    gbm_buy = pickle.load(open('model.pkl','rb'))
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
    gbm_sell = pickle.load(open('model_sell.pkl','rb'))
    result_sell = gbm_sell.predict(to_predict)

    return str(result_buy[0]) + "," + str(result_sell[0])


@app.route('/predict',methods=['POST'])
def predict():
    if request.method == 'POST':

        if W_UPDATE == 'True':
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


if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    # app.run(debug=True)
