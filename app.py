from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import secrets

app = Flask(__name__)

# -----------------------------
# Configuration
# -----------------------------

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


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


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, nullable=False)
    visitor_id = db.Column(db.String(100), nullable=False)


with app.app_context():
    db.create_all()


# -----------------------------
# Home
# -----------------------------
@app.route("/google0b714c2112565072.html")
def google_verification():
    return send_from_directory(".", "google0b714c2112565072.html")

@app.route("/sitemap.xml")
def sitemap():
    sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url><loc>https://dear-nobodyy.onrender.com/</loc></url>
    <url><loc>https://dear-nobodyy.onrender.com/about</loc></url>
    <url><loc>https://dear-nobodyy.onrender.com/stories</loc></url>
</urlset>
"""

    return sitemap_xml, 200, {"Content-Type": "application/xml"}

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

    comments = Comment.query.filter_by(
        story_id=story.id
    ).order_by(Comment.created_at.desc()).all()

    like_count = Like.query.filter_by(
        story_id=story.id
    ).count()

    return render_template(
        "story.html",
        story=story,
        comments=comments,
        like_count=like_count
    )


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

        return redirect(url_for("view_story", story_id=story.id))

    return render_template("new_story.html")


# -----------------------------
# Edit Story
# -----------------------------

@app.route("/edit/<int:story_id>", methods=["GET", "POST"])
def edit_story(story_id):

    if "user" not in session:
        return redirect(url_for("login"))

    story = Story.query.get_or_404(story_id)

    if story.author != session["user"]:
        return "You are not allowed to edit this story."

    if request.method == "POST":

        story.title = request.form["title"]
        story.content = request.form["content"]

        db.session.commit()

        return redirect(url_for("view_story", story_id=story.id))

    return render_template(
        "edit_story.html",
        story=story
    )


# -----------------------------
# Delete Story
# -----------------------------

@app.route("/delete/<int:story_id>", methods=["POST"])
def delete_story(story_id):

    if "user" not in session:
        return redirect(url_for("login"))

    story = Story.query.get_or_404(story_id)

    if story.author != session["user"]:
        return "You are not allowed to delete this story."

    Comment.query.filter_by(story_id=story.id).delete()
    Like.query.filter_by(story_id=story.id).delete()

    db.session.delete(story)
    db.session.commit()

    return redirect(url_for("stories"))


# -----------------------------
# Like Story
# -----------------------------

@app.route("/like/<int:story_id>", methods=["POST"])
def like_story(story_id):

    story = Story.query.get_or_404(story_id)

    if "visitor_id" not in session:
        session["visitor_id"] = secrets.token_hex(16)

    visitor_id = session["visitor_id"]

    existing_like = Like.query.filter_by(
        story_id=story.id,
        visitor_id=visitor_id
    ).first()

    if existing_like:
        db.session.delete(existing_like)
    else:
        new_like = Like(
            story_id=story.id,
            visitor_id=visitor_id
        )

        db.session.add(new_like)

    db.session.commit()

    return redirect(url_for("view_story", story_id=story.id))


# -----------------------------
# Add Comment
# -----------------------------

@app.route("/comment/<int:story_id>", methods=["POST"])
def add_comment(story_id):

    story = Story.query.get_or_404(story_id)

    name = request.form.get("name", "").strip()
    content = request.form.get("content", "").strip()

    if not name or not content:
        return redirect(url_for("view_story", story_id=story.id))

    comment = Comment(
        story_id=story.id,
        name=name,
        content=content
    )

    db.session.add(comment)
    db.session.commit()

    return redirect(url_for("view_story", story_id=story.id))


if __name__ == "__main__":
    app.run()
