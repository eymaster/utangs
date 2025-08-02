from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Debt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20))
    name = db.Column(db.String(100))
    amount = db.Column(db.Float)
    reason = db.Column(db.String(200))
    lender = db.Column(db.String(100))
    status = db.Column(db.Boolean, default=False)

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50))
    detail = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime)
