""" imports all dependencies """
import os
import datetime
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


""" connects flask app to mongoDB and required database """
app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route('/')
def homepage():
    """ injects home page template into the base template
        GET: renders home.html"""
    return render_template('home.html')


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    """ adds a new user to the database
        POST: renders profile.html of new user
        GET: renders sign_up.html"""
    if request.method == 'POST':
        """ check if username already exists in db """
        existing_user = mongo.db.users.find_one(
            {'username': request.form.get('username').lower()})

        if existing_user:
            flash('username already exists')
            return redirect(url_for('sign_up'))

        """ creates new user dictionary in db """
        sign_up = {
            "firstname": request.form.get("firstname").lower(),
            "lastname": request.form.get("lastname").lower(),
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(sign_up)

        """ put the newly created user into a session cookie """
        session["user"] = request.form.get("username").lower()
        flash("you are successfully signed up")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("sign_up.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """ logs an existing user into their profile
    POST: renders profile.html of user
    GET: renders login.html """
    if request.method == "POST":
        """ check if username already exists in db """
        signed_up_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if signed_up_user:
            """ checks input against existing password in db """
            if check_password_hash(
                signed_up_user["password"], request.form.get("password")
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


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    """ retrieves session users username from db
    Args: <username> signed up users username
    POST: renders profile.html of user
    GET: renders login.html """
    user = mongo.db.users.find_one({"username": session["user"]})
    comment = list(mongo.db.comments.find(
        {"comment_author": session["user"]}).sort('comment_datetime', -1))
    books = list(mongo.db.books.find({"post_author": session["user"]}))
    if session["user"]:
        return render_template(
            "profile.html", user=user, comment=comment, books=books)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    """ removes user session cookies which 'logs them out' of session
    GET: renders login.html """
    flash("you've been logged out successfully, come back soon!")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/browse")
def browse():
    """ renders browse template
    GET:  renders browse.html """
    books = list(mongo.db.books.find())
    return render_template("browse.html", books=books)


@app.route("/search", methods=["GET", "POST"])
def search():
    """ retrieves text queries from the db
    GET: renders data sets with matching text in title/author fields """
    query = request.form.get("query")
    books = list(mongo.db.books.find({"$text": {"$search": query}}))
    return render_template('browse.html', books=books)


@app.route("/review/<book_id>")
def review(book_id):
    """ retrieves selected book review and related
    comments(sorted by date) from db"""
    book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    comment = list(mongo.db.comments.find().sort('comment_datetime', -1))
    related_comment = list(mongo.db.comments.find(
        {"book_id": book_id}).sort('comment_datetime', -1)
    )
    if book:
        return render_template(
            "review.html", book=book, comment=comment,
            related_comment=related_comment)
    else:
        return render_template('404.html')


@app.route("/add_review", methods=["GET", "POST"])
def add_review():
    """ adds new book review to db
    GET: renders add_review for signed up users or login for anon user
    POST: successful submission renders browse.html """
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
            return redirect(url_for('browse'))

        return render_template("add_review.html")
    else:
        """ prevents unsigned up/logged out user uploading to db """
        flash('please login to complete this request')
        return redirect(url_for('login'))


@app.route("/edit_review/<book_id>", methods=["GET", "POST"])
def edit_review(book_id):
    """ revises a db entry
    Args: <book_id> id of book review
    GET: if user logged in retrieves their review for editing
    POST: Revises entry and renders browse.html """
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
            return redirect(url_for("browse"))

        return render_template("edit_review.html", book=book)
    else:
        """ prevents anon user editing to db """
        flash('please login to complete this request')
        return redirect(url_for('login'))


@app.route("/delete_review/<book_id>")
def delete_review(book_id):
    """ removes a review from the db
    Args: <book_id> id of book review
    Returns: GET: browse.html on deletion"""
    if 'user' in session:
        mongo.db.books.remove({"_id": ObjectId(book_id)})
        flash("your review was successfully deleted")
        return redirect(url_for("browse"))
    else:
        """ prevents anon user removing entry from db """
        flash('please login to complete this request')
        return redirect(url_for('login'))


@app.route("/add_comment/<book_id>", methods=["GET", "POST"])
def add_comment(book_id):
    """ allows logged in user to upload a comment
    Args: <book_id> id of book review
        Returns: GET renders add_comment.html
    POST on successful submission renders browse.html """
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
            return redirect(url_for("browse"))

        book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
        return render_template("add_comment.html", book=book)
    else:
        """ prevents anon user from uploading """
        flash('please login to complete this request')
        return redirect(url_for('login'))


@app.route('/delete_comment/<comment_id>')
def delete_comment(comment_id):
    """ allows logged in user to delete their own comments
    Args <comment_id> id of comment in db
    Returns GET: on successful submission browse.html """
    if 'user' in session:
        mongo.db.comments.remove({'_id': ObjectId(comment_id)})
        flash('your comment was successfully deleted')
        return redirect(url_for('browse'))
    else:
        """ prevents anon from deleting """
        flash('please login to complete this request')
        return redirect(url_for('login'))


# code found in flask documentation
@app.errorhandler(404)
def page_not_found(error):
    """ handles unfound data errors
    Arg: 404 error code
    Returns: GET renders 404.html """
    return render_template('404.html', error=error), 404


@app.errorhandler(500)
def internal_server_error(error):
    """ handles internal server errors
    Arg: 500 error code
    Returns: GET renders 500.html """
    return render_template('500.html', error=error), 500


if __name__ == '__main__':
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
