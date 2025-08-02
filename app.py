
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import aliased
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

class Debt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    name_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    lender_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    amount = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Boolean, default=False)
    name = db.relationship("Person", foreign_keys=[name_id], backref="debts")
    lender = db.relationship("Person", foreign_keys=[lender_id])

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(20))
    debt_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text)

@app.route('/', methods=['GET', 'POST'])
def index():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()

    if request.method == 'POST' and 'table_name' in request.form:
        table_name = request.form.get('table_name')
        if table_name:
            try:
                db.session.execute(text(f'DROP TABLE IF EXISTS "{table_name}"'))
                db.session.commit()
                flash(f'Table "{table_name}" dropped successfully.', 'danger')
            except Exception as e:
                flash(str(e), 'warning')
        return redirect(url_for('index'))

    return render_template('index.html', tables=tables)

@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"]
    lender = request.form["lender"]
    amount = float(request.form["amount"])
    reason = request.form["reason"]
    status = "status" in request.form

    person_name = Person.query.filter_by(name=name).first()
    if not person_name:
        person_name = Person(name=name)
        db.session.add(person_name)

    person_lender = Person.query.filter_by(name=lender).first()
    if not person_lender:
        person_lender = Person(name=lender)
        db.session.add(person_lender)

    db.session.commit()

    debt = Debt(name_id=person_name.id, lender_id=person_lender.id, amount=amount, reason=reason, status=status)
    db.session.add(debt)
    db.session.commit()

    history = History(action="add", debt_id=debt.id, details=f"Added debt for {name} amount {amount}")
    db.session.add(history)
    db.session.commit()

    return jsonify({"success": True})

@app.route("/toggle-theme", methods=["POST"])
def toggle_theme():
    return jsonify({"message": "Theme toggled"})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)


@app.route("/split", methods=["POST"])
def split():
    amount = float(request.form["split_amount"])
    reason = request.form["split_reason"]
    lender = request.form["split_lender"]
    selected_names = request.form.getlist("split_names")

    lender_obj = Person.query.filter_by(name=lender).first()
    if not lender_obj:
        lender_obj = Person(name=lender)
        db.session.add(lender_obj)
        db.session.commit()

    split_amount = round(amount / len(selected_names), 2)
    for name in selected_names:
        person = Person.query.filter_by(name=name).first()
        if not person:
            person = Person(name=name)
            db.session.add(person)
            db.session.commit()

        debt = Debt(name_id=person.id, lender_id=lender_obj.id, amount=split_amount, reason=reason)
        db.session.add(debt)
        db.session.commit()

        history = History(action="split_add", debt_id=debt.id, details=f"Split debt for {name} amount {split_amount}")
        db.session.add(history)
        db.session.commit()

    return jsonify({"success": True})


# One-time init route to create tables
#@app.route('/initdb')
def initdb():
    db.create_all()
    return "Database tables created nyeee."
