from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')  # Provided by Render
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
class User(db.Model):
    __tablename__ = 'users'  # safer and clearer

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# Define database model
#class User(db.Model):
   # id = db.Column(db.Integer, primary_key=True)
   # name = db.Column(db.String(100), nullable=False)

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        user = User(name=name)
        db.session.add(user)
        db.session.commit()
        return redirect('/users')
    return render_template('index.html')

@app.route('/users')

def users():
    all_users = User.query.all()
    return render_template('users.html', users=all_users)


if __name__ == '__main__':
    app.run(debug=True)
