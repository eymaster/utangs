from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///debts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Debt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    amount = db.Column(db.Float)
    reason = db.Column(db.String(120))
    status = db.Column(db.String(20), default='Pending')

class HistoryLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    action = db.Column(db.String(200))

# Home Page
@app.route('/')
def index():
    people = db.session.query(Debt.name).distinct().all()
    return render_template('index.html', all_names=[p[0] for p in people])

# Debts Page
@app.route('/debts')
def show_debts():
    name_filter = request.args.get('name')
    query = Debt.query
    if name_filter:
        query = query.filter_by(name=name_filter)
    debts = query.order_by(Debt.id.desc()).all()

    # Summary: total unpaid by person
    summary = db.session.query(Debt.name, func.sum(Debt.amount))\
        .filter(Debt.status == 'Pending')\
        .group_by(Debt.name).all()

    history_logs = HistoryLog.query.order_by(HistoryLog.timestamp.desc()).limit(50).all()

    people = db.session.query(Debt.name).distinct().all()

    return render_template('debts.html',
        debts=debts,
        debts_summary=summary,
        history_logs=history_logs,
        all_names=[p[0] for p in people],
        name_filter=name_filter
    )

# Add Debt
@app.route('/add', methods=['POST'])
def add_debt():
    name = request.form['name']
    amount = float(request.form['amount'])
    reason = request.form['reason']
    status = request.form['status']
    new_debt = Debt(name=name, amount=amount, reason=reason, status=status)
    db.session.add(new_debt)
    db.session.add(HistoryLog(action=f"Added debt for {name} (₱{amount:.2f}) — {reason}"))
    db.session.commit()
    return redirect('/debts')

# Edit Debt
@app.route('/edit/<int:id>', methods=['POST'])
def edit_debt(id):
    debt = Debt.query.get_or_404(id)
    old_data = f"{debt.name} (₱{debt.amount:.2f}) — {debt.reason} — {debt.status}"

    debt.name = request.form['name']
    debt.amount = float(request.form['amount'])
    debt.reason = request.form['reason']
    debt.status = request.form['status']

    new_data = f"{debt.name} (₱{debt.amount:.2f}) — {debt.reason} — {debt.status}"

    if old_data != new_data:
        db.session.add(HistoryLog(action=f"Edited debt: {old_data} → {new_data}"))

    db.session.commit()
    return redirect('/debts')

# Delete Debt (AJAX-safe)
@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_debt(id):
    debt = Debt.query.get_or_404(id)
    log_text = f"Deleted debt for {debt.name} (₱{debt.amount:.2f}) — {debt.reason} — {debt.status}"
    db.session.delete(debt)
    db.session.add(HistoryLog(action=log_text))
    db.session.commit()
    return jsonify({"success": True})

# API Endpoint for Live Summary + Filtered Debts
@app.route('/debts_data')
def debts_data():
    name = request.args.get('name')
    query = Debt.query
    if name:
        query = query.filter_by(name=name)

    debts = query.order_by(Debt.id.desc()).all()

    summary = (
        db.session.query(Debt.name, func.sum(Debt.amount))
        .filter(Debt.status == 'Pending')
        .group_by(Debt.name)
        .all()
    )

    unpaid_total = sum(debt.amount for debt in debts if debt.status == 'Pending')

    return jsonify({
        "debts": [{
            "id": d.id,
            "name": d.name,
            "amount": d.amount,
            "reason": d.reason,
            "status": d.status
        } for d in debts],
        "summary": [{"name": s[0], "amount": s[1]} for s in summary],
        "unpaid_total": unpaid_total
    })

@app.route('/init_db')
def init_db():
    db.create_all()
    return "Database initialized!"
# Initialize DB (Fixed)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

# Run the app
#if __name__ == '__main__':
   # app.run(debug=True)
