
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text
import os

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')  # Render sets this
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#db = SQLAlchemy(app)
app.config['SECRET_KEY'] = '5f3fba401aebfa99c3b6794dc22d7d5111ae21d194712b5e67a6ab89f1bc4fd8'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')  # Render sets this
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///utang.db'
db = SQLAlchemy(app)

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

@app.route('/drop-all-tables', methods=['POST'])
def drop_all_tables():
    db.drop_all()
    flash('All tables dropped successfully!', 'danger')
    return redirect(url_for('index'))

@app.route('/create-table', methods=['POST'])
def create_table():
    new_table = request.form.get('new_table_name')
    columns = request.form.get('columns')

    if not new_table or not columns:
        flash('Please provide table name and columns.', 'warning')
        return redirect(url_for('index'))

    try:
        create_sql = f"CREATE TABLE {new_table} ({columns})"
        db.session.execute(text(create_sql))
        db.session.commit()
        flash(f'Table "{new_table}" created successfully!', 'success')
    except Exception as e:
        flash(f"Error creating table: {e}", 'danger')

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
