from flask import Flask, redirect, url_for, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/ruchijain'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
print("ruchi")
db = SQLAlchemy(app)

# Database Model
class user(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    meg = db.Column(db.String(120), nullable=True)

with app.app_context():
    db.create_all()
    
@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            # Retrieving data from the form
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            message = request.form.get('message')
            
            # Adding the entry to the database
            entry = user(name=name, email=email, phone_num=phone, meg=message)
            db.session.add(entry)
            db.session.commit()
            print("Data successfully added!")
        except Exception as e:
            print("Failed to add data to the database. Error:", e)
    return render_template('contact.html')

@app.route("/contacts")
def contacts():
    # Retrieving all entries from the Contacts table
    all_contacts = user.query.all()
    
    return render_template('contacts.html', contacts=all_contacts)


if __name__ == "__main__":
    # Run the Flask app
    app.run(debug=True)