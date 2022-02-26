from database import db
from sqlalchemy import and_, asc, desc

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


def get_tick_data():
    tick_data = TICK.query.order_by(desc(TICK.id)).limit(200)
    return tick_data


def regist_tick(ticks):
    curr = []
    curr = TICK.query.filter(TICK.time==ticks['time']).all()
    if(len(curr) == 0):
        items_idx = list()
        item = dict()
        item['currency'] = ticks['curr']
        item['period'] = ticks['perd']
        item['time'] = ticks['time']
        item['open'] = ticks['open']
        item['high'] = ticks['high']
        item['low'] = ticks['low']
        item['close'] = ticks['close']
        items_idx.append(item)

        db.session.execute(TICK.__table__.insert(), items_idx)
        db.session.commit()
