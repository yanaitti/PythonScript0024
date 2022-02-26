import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Database Connection
def init_db(app):
    db.init_app(app)
