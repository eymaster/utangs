from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models import db, Debt, History
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')  # Render sets this
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///utang.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    debts = Debt.query.order_by(Debt.date.desc()).all()
    history = History.query.order_by(History.timestamp.desc()).all()
    names = sorted({d.name for d in debts})
    lenders = sorted({d.lender for d in debts})
    return render_template('index.html', debts=debts, history=history, names=names, lenders=lenders)

@app.route('/add', methods=['POST'])
def add():
    data = request.json
    date = data['date']
    name = data['name']
    amount = float(data['amount'])
    reason = data['reason']
    lender = data['lender']
    status = data['status'] == 'true'
    new_debt = Debt(date=date, name=name, amount=amount, reason=reason, lender=lender, status=status)
    db.session.add(new_debt)
    db.session.commit()
    log = History(action='Add', detail=f'{name} owes {amount} for {reason} from {lender}', timestamp=datetime.now())
    db.session.add(log)
    db.session.commit()
    return jsonify({'message': 'Added'})

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    debt = Debt.query.get(id)
    db.session.delete(debt)
    db.session.commit()
    log = History(action='Delete', detail=f'Deleted debt from {debt.name}', timestamp=datetime.now())
    db.session.add(log)
    db.session.commit()
    return jsonify({'message': 'Deleted'})

@app.route('/edit/<int:id>', methods=['POST'])
def edit(id):
    debt = Debt.query.get(id)
    data = request.json
    debt.name = data['name']
    debt.amount = float(data['amount'])
    debt.reason = data['reason']
    debt.lender = data['lender']
    debt.status = data['status'] == 'true'
    db.session.commit()
    log = History(action='Edit', detail=f'Edited debt of {debt.name}', timestamp=datetime.now())
    db.session.add(log)
    db.session.commit()
    return jsonify({'message': 'Updated'})

# One-time init route to create tables
@app.route('/initdb')
def initdb():
    db.create_all()
    return "Database tables created nyeee."

if __name__ == '__main__':
    app.run(debug=True)
