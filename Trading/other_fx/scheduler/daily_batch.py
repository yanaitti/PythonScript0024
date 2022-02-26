import os
import datetime
import logging
from sqlalchemy import *
from sqlalchemy.orm import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get('DATABASE_URL',
                              'postgresql://llgcrvdkorbylq:14873167399cd4c3a19a7d9710fa425014e7a0881fc764d9c36be0f92ce31bf2@ec2-3-212-75-25.compute-1.amazonaws.com:5432/d7sd96eoncd2or')

ENGINE = create_engine(
    DATABASE_URL,
    encoding = "utf-8",
    echo=True # Trueだと実行のたびにSQLが出力される
)

# Sessionの作成
session = scoped_session(
    # ORM実行時の設定。自動コミットするか、自動反映するなど。
    sessionmaker(
        autocommit = False,
        autoflush = False,
        bind = ENGINE
    )
)

def main():
    session.execute('delete from t_tick c where'\
        ' exists ('\
        ' select a.id from t_tick a'\
        ' left outer join (select id from t_tick b order by id desc limit 1000) b on a.id = b.id'\
        ' where b.id is null and c.id = a.id'\
        ')')
    session.commit()
    logger.info('daily batch complete.')


if __name__ == '__main__':
    main()
