from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# -----------------------------
# Configuration
# -----------------------------
app.config["SECRET_KEY"] = "joe_blog_secret_key_2026"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# -----------------------------
# Database Model
# -----------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


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
    return render_template("stories.html")


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
# -----------------------------
# Create Admin
# -----------------------------
@app.route("/create_admin")
def create_admin():

    # Delete all existing users
    User.query.delete()
    db.session.commit()

    # Create new admin
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
@app.route("/new")
def new_story():
    return render_template("new_story.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)