from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os
from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import func  # at the top of your file
# ... (existing imports and config)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')  # Render sets this
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database model
class Debt(db.Model):
    __tablename__ = 'debts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(200), nullable=False)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        amount = float(request.form['amount'])
        reason = request.form['reason']
        db.session.add(Debt(name=name, amount=amount, reason=reason))
        db.session.commit()
        return redirect('/debts')
    return render_template('index.html')

@app.route('/debts')
def debts():
    all_debts = Debt.query.all()
    # return render_template('debts.html', debts=all_debts)
    # Group by person and sum their debt
    debts_summary = (
        db.session.query(Debt.name, func.sum(Debt.amount))
        .group_by(Debt.name)
        .all()
    )
    
    # Total debt across all people
    total_debt = db.session.query(func.sum(Debt.amount)).scalar() or 0

    return render_template("debts.html", debts=all_debts, debts_summary=debts_summary, total_debt=total_debt)


# DELETE route
@app.route('/delete/<int:debt_id>')
def delete(debt_id):
    debt = Debt.query.get_or_404(debt_id)
    db.session.delete(debt)
    db.session.commit()
    return redirect('/debts')

# EDIT route - show form
@app.route('/edit/<int:debt_id>', methods=['GET', 'POST'])
def edit(debt_id):
    debt = Debt.query.get_or_404(debt_id)
    if request.method == 'POST':
        debt.name = request.form['name']
        debt.amount = float(request.form['amount'])
        debt.reason = request.form['reason']
        db.session.commit()
        return redirect('/debts')
    return render_template('edit.html', debt=debt)
# One-time init route to create tables
#@app.route('/initdb')
def initdb():
    db.create_all()
    return "Database tables created nyeee."

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    
