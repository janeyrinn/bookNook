""" imports all dependencies """
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

""" connects app to mongoDB and required database """
app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


""" injects home page template into the base template """


@app.route("/")
def homepage():

    return render_template("home.html")


""" adds a new user to the database
POST: renders profile.html of new user
GET: renders register.html to register user"""


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        """ check if username already exists in db """
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("username already exists")
            return redirect(url_for("register"))

        """ creates new user dictionary in db """
        register = {
            "firstname": request.form.get("firstname").lower(),
            "lastname": request.form.get("lastname").lower(),
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        """ put the newly created user into a session cookie """
        session["user"] = request.form.get("username").lower()
        flash("you are successfully registered")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


""" logs an existing user into their profile
POST: renders profile.html of user
GET: renders login.html """


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        """ check if username already exists in db """
        registered_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if registered_user:
            """ checks input against existing password in db """
            if check_password_hash(
                registered_user["password"], request.form.get("password")
            ):
                session["user"] = request.form.get("username").lower()
                flash("Welcome back, {}".format(
                    request.form.get("username")))
                return redirect(url_for(
                    "profile", username=session["user"]))
            else:
                """ error message for invalid password entry """
                flash("Oops check your username/password and try again")
                return redirect(url_for("login"))

        else:
            """ no match for username """
            flash("Oops check your username/password and try again")
            return redirect(url_for("login"))

    return render_template("login.html")


""" retrieves session users username from db
Args: <username> registerered users username
POST: renders profile.html of user
GET: renders login.html """


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):

    user = mongo.db.users.find_one({"username": session["user"]})
    if session["user"]:
        return render_template("profile.html", user=user)

    return redirect(url_for("login"))


""" removes user session cookies which 'logs them out' of session
GET: renders login.html """


@app.route("/logout")
def logout():

    flash("you've been logged out successfully, come back soon!")
    session.pop("user")
    return redirect(url_for("login"))


""" renders search template
GET:  renders search.html """


@app.route("/search")
def search():
    books = list(mongo.db.books.find())
    return render_template("search.html", books=books)


""" retrieves text queries from the db
GET: renders data sets with matching text in title/author fields """


@app.route("/filter", methods=["GET", "POST"])
def filter():
    query = request.form.get("query")
    books = list(mongo.db.books.find({"$text": {"$search": query}}))
    return render_template("search.html", books=books)


""" retrieves selected book review from db """


@app.route("/review/<book_id>")
def review(book_id):

    book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    comment = list(mongo.db.comments.find())
    if book:
        return render_template("review.html", book=book, comment=comment)
    else:
        return render_template('404.html')


""" adds new book review to db
GET: renders add_review for reg' users or login for unregistered
POST: successful submission renders search.html """


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
            return redirect(url_for('search'))

        return render_template("add_review.html")
    else:
        """ prevents unregistered/logged out user uploading to db """
        flash('please login to complete this request')
        return redirect(url_for('login'))


""" revises a db entry
Args: <book_id> id of book review
GET: if user logged in retrieves their review for editing
POST: Revises entry and renders search.html """


@app.route("/edit_review/<book_id>", methods=["GET", "POST"])
def edit_review(book_id):
    book = mongo.db.books.find_one({"_id": ObjectId(book_id)})

    if 'user' in session:
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
    else:
        """ prevents unregistered/logged out user editing to db """
        flash('please login to complete this request')
        return redirect(url_for('login'))


""" removes a review from the db
Args: <book_id> id of book review
Returns: GET: search.html on deletion"""


@app.route("/delete_review/<book_id>")
def delete_review(book_id):

    if 'user' in session:
        mongo.db.books.remove({"_id": ObjectId(book_id)})
        flash("your review was successfully deleted")
        return redirect(url_for("search"))
    else:
        """ prevents unregistered/logged out user removing entry from db """
        flash('please login to complete this request')
        return redirect(url_for('login'))


""" allows logged in user to upload a comment
Args: <book_id> id of book review
Returns: GET renders add_comment.html
POST on successful submission renders search.html """


@app.route("/add_comment/<book_id>", methods=["GET", "POST"])
def add_comment(book_id):
    if 'user' in session:
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
    else:
        """ prevents unregistered/logged in from uploading """
        flash('please login to complete this request')
        return redirect(url_for('login'))


""" allows logged in user to delete their own comments
Args <comment_id> id of comment in db
Returns GET: on successful submission search.html """


@app.route('/delete_comment/<comment_id>')
def delete_comment(comment_id):

    if 'user' in session:
        mongo.db.comments.remove({'_id': ObjectId(comment_id)})
        flash('your comment was successfully deleted')
        return redirect(url_for('search'))
    else:
        """ prevents unregistered/logged in from deleting """
        flash('please login to complete this request')
        return redirect(url_for('login'))


""" handles unfound data errors
Arg: 404 error code
Returns: GET renders 404.html """


# code found in flask documentation
@app.errorhandler(404)
def page_not_found(e):

    return render_template('404.html', e=e), 404


""" handles internal server errors
Arg: 500 error code
Returns: GET renders 500.html """


@app.errorhandler(500)
def internal_server_error(e):

    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
