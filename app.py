from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os
from flask import jsonify
from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import func  # at the top of your file
# ... (existing imports and config)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')  # Render sets this
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database model
class Debt(db.Model):
    __tablename__ = 'debt'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get("new_name") or request.form.get("existing_name")
        #name = request.form['name']
        amount = float(request.form['amount'])
        reason = request.form['reason']
        status = request.form['status']  # get status
        db.session.add(Debt(name=name, amount=amount, reason=reason, status=status))
        db.session.commit()
        #flash('Debt added successfully!', 'success')
        #return redirect('/index')
        #return redirect(url_for('index'))
        #if name and amount and reason:
            #new_debt = Debt(name=name, amount=float(amount), reason=reason)
           # db.session.add(new_debt)
            #db.session.commit
            # return redirect(url_for('index'))
            #debts.append({
            #    'name': name,
              #  'amount': float(amount),
               # 'reason': reason
            #})
            
           # flash('Debt added successfully!', 'success')
            #return redirect(url_for('index'))
    #return render_template('index.html', debts=debts)
    
        #return redirect('/debts')

    debts_summary = db.session.query(Debt.name,db.func.sum(Debt.amount)).filter(Debt.status == 'Pending').group_by(Debt.name).all()
    
    # Total debt across all people
    total_debt = db.session.query(func.sum(Debt.amount)).scalar() or 0

    all_names = db.session.query(Debt.name).distinct().all()
    all_names = [name for (name,) in all_names]  # flatten tuples

   # return render_template('index.html')
    return render_template('index.html', debts_summary=debts_summary, total_debt=total_debt, all_names=all_names)

@app.route('/debts')
def debts():
    all_debts = Debt.query.all()
    name_filter = request.args.get('name')
    # Get list of unique names for dropdown
    try:
        all_names = [row[0] for row in db.session.query(Debt.name).distinct().all()]
    except Exception as e:
        all_names = []
        print("Error loading names:", e)
    #all_names = [row[0] for row in db.session.query(Debt.name).distinct().all()]
    query = Debt.query

    if name_filter:
        query = query.filter(Debt.name == name_filter)

    # Sort Pending first
    all_debts = query.order_by(Debt.status.desc()).all()
    
    # return render_template('debts.html', debts=all_debts)
    # Group by person and sum their debt
    #debts_summary = (db.session.query(Debt.name, func.sum(Debt.amount)).group_by(Debt.name).all())
    
    # Total debt across all people
    total_debt = db.session.query(func.sum(Debt.amount)).scalar() or 0
    unpaid_total = sum(debt.amount for debt in all_debts if debt.status == 'Pending')
    # Show only unpaid totals per person
    debts_summary = db.session.query(Debt.name,db.func.sum(Debt.amount)).filter(Debt.status == 'Pending').group_by(Debt.name).all()
    return render_template(
        "debts.html",
        debts=all_debts,
        debts_summary=debts_summary,
        total_debt=total_debt,  # Optional if you don't use it anymore
        unpaid_total=unpaid_total,
        name_filter=name_filter,
        all_names=all_names)

    #return render_template("debts.html", debts=all_debts, debts_summary=debts_summary, total_debt=total_debt)


@app.route('/toggle_status/<int:debt_id>', methods=['POST'])
def toggle_status(debt_id):
    data = request.get_json()
    new_status = data.get('status')

    debt = Debt.query.get_or_404(debt_id)
    debt.status = new_status
    db.session.commit()
    return jsonify({'success': True})


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
        debt.status = request.form['status']
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
    
