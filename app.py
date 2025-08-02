from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///debts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Debt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    amount = db.Column(db.Float)
    reason = db.Column(db.String(200))
    lender = db.Column(db.String(100))
    status = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    debts = Debt.query.all()
    return render_template('index.html', debts=debts)

@app.route('/add', methods=['POST'])
def add_debt():
    data = request.json
    new_debt = Debt(
        name=data['name'],
        amount=data['amount'],
        reason=data['reason'],
        lender=data['lender'],
        status=data.get('status', False)
    )
    db.session.add(new_debt)
    db.session.commit()
    return jsonify({'success': True, 'id': new_debt.id})

@app.route('/edit/<int:id>', methods=['POST'])
def edit_debt(id):
    data = request.json
    debt = Debt.query.get_or_404(id)
    debt.name = data['name']
    debt.amount = data['amount']
    debt.reason = data['reason']
    debt.lender = data['lender']
    debt.status = data['status']
    db.session.commit()
    return jsonify({'success': True})

@app.route('/delete/<int:id>', methods=['POST'])
def delete_debt(id):
    debt = Debt.query.get_or_404(id)
    db.session.delete(debt)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/toggle_status/<int:id>', methods=['POST'])
def toggle_status(id):
    debt = Debt.query.get_or_404(id)
    debt.status = not debt.status
    db.session.commit()
    return jsonify({'success': True, 'status': debt.status})

@app.route('/data')
def get_data():
    debts = Debt.query.all()
    data = [{
        'id': d.id,
        'name': d.name,
        'amount': d.amount,
        'reason': d.reason,
        'lender': d.lender,
        'status': d.status
    } for d in debts]
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
