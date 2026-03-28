import os
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "nassar_dev_2026" 

# إعدادات الداتا بيز (SQLite للتجربة و PostgreSQL للرفع)
db_url = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/img'

db = SQLAlchemy(app)

# --- الجداول ---
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    message = db.Column(db.Text)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    service = db.Column(db.String(100))

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    image_url = db.Column(db.String(500))

with app.app_context():
    db.create_all()

# --- المسارات ---
@app.route("/")
def home():
    projects = Project.query.all()
    return render_template("index.html", projects=projects)

@app.route("/send", methods=["POST"])
def send():
    new_msg = Message(name=request.form.get("name"), email=request.form.get("email"), message=request.form.get("message"))
    db.session.add(new_msg)
    db.session.commit()
    return redirect("/")

@app.route("/order", methods=["POST"])
def order():
    new_order = Order(name=request.form.get("name"), service=request.form.get("service"))
    db.session.add(new_order)
    db.session.commit()
    return redirect("/")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form.get("username") == "admin" and request.form.get("password") == "1234":
            session["admin"] = True
            return redirect("/admin")
    return render_template("login.html")

@app.route("/admin")
def admin():
    if not session.get("admin"): return redirect("/login")
    return render_template("admin.html", messages=Message.query.all(), orders=Order.query.all())

@app.route("/add_project", methods=["POST"])
def add_project():
    if not session.get("admin"): return redirect("/login")
    file = request.files['image']
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        db.session.add(Project(title=request.form.get("title"), image_url=filename))
        db.session.commit()
    return redirect("/admin")

@app.route("/delete/<string:type>/<int:id>")
def delete_item(type, id):
    if not session.get("admin"): return redirect("/login")
    item = Message.query.get(id) if type == "msg" else Order.query.get(id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect("/admin")

if __name__ == "__main__":
    app.run(debug=True)