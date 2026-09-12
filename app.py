from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

# -----------------------------
# Configuration
# -----------------------------
import os
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
with app.app_context():
    db.create_all()


# -----------------------------
# Database Models
# -----------------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# -----------------------------
# Home
# -----------------------------

@app.route("/")
def home():
return render_template("index.html")


# -----------------------------
# About
# -----------------------------

@app.route("/about")
def about():
return render_template("about.html")


# -----------------------------
# Stories
# -----------------------------

@app.route("/stories")
def stories():
posts = Story.query.order_by(Story.created_at.desc()).all()
return render_template("stories.html", posts=posts)


# -----------------------------
# View Single Story
# -----------------------------

@app.route("/story/<int:story_id>")
def view_story(story_id):
story = Story.query.get_or_404(story_id)
return render_template("story.html", story=story)


# -----------------------------
# Login
# -----------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

if request.method == "POST":

username = request.form.get("username")
password = request.form.get("password")

user = User.query.filter_by(username=username).first()

if user and check_password_hash(user.password, password):
session["user"] = username
return redirect(url_for("dashboard"))

return render_template(
"login.html",
error="Invalid Username or Password"
)

return render_template("login.html")


# -----------------------------
# Dashboard
# -----------------------------

@app.route("/dashboard")
def dashboard():

if "user" not in session:
return redirect(url_for("login"))

return render_template(
"dashboard.html",
username=session["user"]
)


# -----------------------------
# Logout
# -----------------------------

@app.route("/logout")
def logout():

session.pop("user", None)

return redirect(url_for("home"))


# -----------------------------
# Create Admin
# -----------------------------

@app.route("/create_admin")
def create_admin():

User.query.delete()

db.session.commit()

admin = User(
username="joe",
password=generate_password_hash("mysecret123")
)

db.session.add(admin)
db.session.commit()

return "New admin created successfully!"


# -----------------------------
# New Story
# -----------------------------
@app.route("/new", methods=["GET", "POST"])
def new_story():

    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        title = request.form["title"]
        content = request.form["content"]

        story = Story(
            title=title,
            content=content,
            author=session["user"]
        )

        db.session.add(story)
        db.session.commit()

        return redirect("/stories")

    return render_template("new_story.html")       


