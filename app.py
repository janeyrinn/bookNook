# imports all dependencies
import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env
import datetime

# connects app to mongoDB and required database
app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
def homepage():
    # injects home page template into the base template
    return render_template("home.html")


# adds a new user to the database
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("username already exists")
            return redirect(url_for("register"))

        # creates new user dictionary in db
        register = {
            "firstname": request.form.get("firstname").lower(),
            "lastname": request.form.get("lastname").lower(),
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the newly created user into a session cookie
        session["user"] = request.form.get("username").lower()
        flash("you are successfully registered")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


# logs an existing user into their profile
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username already exists in db
        registered_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if registered_user:
            # checks input against existing password in db
            if  check_password_hash(
                registered_user["password"],
                    request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome back, {}".format(
                        request.form.get("username")))
                    return redirect(url_for(
                        "profile", username=session["user"]))
            else:
                # error message for invalid password entry
                flash("Oops check your username/password and try again")
                return redirect(url_for("login"))

        else:
            # no match for username
            flash("Oops check your username/password and try again")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # retrieves session users username from db
    user = mongo.db.users.find_one(
        {"username": session["user"]})

    if session["user"]:
        return render_template("profile.html", user=user)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # removes user session cookies which 'logs them out' of session
    flash("you've been logged out successfully, come back soon!")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/search")
def search():
    books = list(mongo.db.books.find())
    return render_template("search.html", books=books)


@app.route("/filter", methods=["GET", "POST"])
def filter():
    query = request.form.get("query")
    books = list(mongo.db.books.find({"$text": {"$search": query}}))
    return render_template("search.html", books=books)


@app.route("/review/<book_id>")
def review(book_id):
    book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    comment = list(mongo.db.comments.find())
    return render_template("review.html", book=book, comment=comment)


@app.route("/add_review", methods=["GET", "POST"])
def add_review():

    if 'user' in session:
        if request.method == "POST":
            book = {
                "book_title": request.form.get("book_title").lower(),
                "book_author": request.form.get("book_author").lower(),
                "book_review": request.form.get("book_review").lower(),
                "book_link": request.form.get("book_link"),
                "book_img": request.form.get("book_img"),
                "post_author": session["user"]
            }
            mongo.db.books.insert_one(book)
            flash("Your book review was successfully added")
            return redirect(url_for("add_review"))

        return render_template("add_review.html")
    else:
        return redirect(url_for('login'))


@app.route("/edit_review/<book_id>", methods=["GET", "POST"])
def edit_review(book_id):
    book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    if request.method == "POST":
        revised = {
            "book_title": request.form.get("book_title").lower(),
            "book_author": request.form.get("book_author").lower(),
            "book_review": request.form.get("book_review").lower(),
            "book_link": request.form.get("book_link"),
            "book_img": request.form.get("book_img"),
            "post_author": session["user"]
        }
        mongo.db.books.update({"_id": ObjectId(book_id)}, revised)
        flash("Your book review was successfully updated")
        return redirect(url_for("search"))

    return render_template("edit_review.html", book=book)


@app.route("/delete_review/<book_id>")
def delete_review(book_id):
    mongo.db.books.remove({"_id": ObjectId(book_id)})
    flash("your review was successfully deleted")
    return redirect(url_for("search"))


@app.route("/add_comment/<book_id>", methods=["GET", "POST"])
def add_comment(book_id):
    if request.method == "POST":
        comment = {
            "book_id": book_id,
            "comment_datetime": datetime.datetime.now().strftime(
                '%d %B %Y - %H:%M:%S'),
            "comment_title": request.form.get("comment_title").lower(),
            "comment": request.form.get("comment").lower(),
            "comment_author": session["user"]
        }
        mongo.db.comments.insert_one(comment)
        flash("your comment was successfully added")
        return redirect(url_for("search"))

    book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    return render_template("add_comment.html", book=book)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
