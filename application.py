import os
from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_bootstrap import Bootstrap
from flask import abort
import requests
import json


app = Flask(__name__)
Bootstrap(app)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


# 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

#403
@app.errorhandler(403)
def page_not_found(e):
    return render_template("403.html"), 403


@app.route("/<string:error>")
def error(error):
    return abort(404)

#index login page
@app.route("/")
def index():
    if session.get('logged_in') != True:
        return render_template("login.html")
    else:
        u = session['user']
        return render_template("index.html", us = u)

#registration page
@app.route("/register")
def register():
    return render_template("registration.html")

# registeration intermediate page
@app.route("/reg", methods=["POST"])
def reg():
        name = request.form.get("name")
        email = request.form.get("email")
        uname = request.form.get("username")
        password = request.form.get("password")
        if db.execute("SELECT * FROM credentials WHERE email = :email and uname= :uname", {"email": email, "uname": uname}).rowcount == 0:  #check if email or username is already exist or not.
            db.execute("INSERT INTO credentials (name, email, uname, password) VALUES (:name, :email, :uname, :password)",
                {"name": name, "email": email, "uname": uname, "password": password})    #register for name username email password.
            db.commit()
            return render_template("registration.html", message="Congratulations! you Successfully Registered")
        else:
            return render_template("registration.html", message="USERNAME or Email-ID already exist!")


# login intermediate (credential checking)
@app.route("/login", methods=["POST"])
def login():
        user = request.form.get("user")
        passw = request.form.get("passw")
        if db.execute("SELECT * FROM credentials WHERE uname = :uname and password= :password", {"uname": user, "password": passw}).rowcount == 1: #verify email password
            session['user'] = user
            session['logged_in'] = True
            u = session['user']
            return render_template("index.html", us = u)
        else:
            return render_template("login.html", message="USERNAME or PASSWORD incorrect.")


# logout intermediate page
@app.route("/logout", methods=["POST"])
def logout():
        session.pop('user', None)
        session.clear()
        return render_template("login.html")

# data search intermediate page
@app.route("/search", methods=["POST"])
def search():
    if session.get('logged_in') != True:
       return abort(403)
    else:
        u = session['user'];
        isbn = request.form.get("isbn").lower().strip()
        title = request.form.get("title").lower().strip()
        author = request.form.get("author").lower().strip()
        books = db.execute("SELECT * from books where LOWER(isbn) like :isbn and LOWER(author) like :author and LOWER(title) like :title", {"isbn": f"%{isbn}%", "author": f"%{author}%", "title": f"%{title}%"}).fetchall()
        return render_template("result.html", books = books, us = u)


# book information
@app.route("/book/<string:id_book>")
def bookdata(id_book):
     if session.get('logged_in') != True:
        return abort(403)
     else:
        if db.execute("SELECT * FROM books WHERE id_book = :id_book", {"id_book": id_book}).rowcount == 0:
            return abort(404)
        else:
            u = session['user'];
            bookdetail = db.execute("SELECT * FROM books WHERE id_book = :id_book", {"id_book": id_book}).fetchone()
            res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "EKV1ySYo9Wbugb1ZQGbA", "isbns": bookdetail.isbn}).json()
            revi = db.execute("SELECT rev_username, review, rating FROM reviews WHERE rev_book_id = :rev_book_id", {"rev_book_id": id_book}).fetchall()
            return render_template("review.html", bookdetail = bookdetail, res=res['books'][0], us=u, revi=revi)


@app.route("/review/<string:id_book>", methods=["POST"])
def review(id_book):
    if session.get('logged_in') != True:
       return abort(403)
    else:
        rev_username = session['user'];
        rating = request.form.get("rating")
        review = request.form.get("review")
        rev_book_id = id_book

        if db.execute("SELECT * FROM reviews WHERE rev_username = :rev_username and rev_book_id = :rev_book_id", {"rev_username": rev_username, "rev_book_id": rev_book_id}).rowcount == 0:
            db.execute("INSERT INTO reviews (rev_book_id, rev_username, review, rating) VALUES ( :rev_book_id, :rev_username, :review, :rating)",
                { "rev_book_id": rev_book_id, "rev_username": rev_username, "review": review, "rating": rating})
            db.commit()
            message = "THANKYOU FOR YOUR REVIEWED!"
            bookdetail = db.execute("SELECT * FROM books WHERE id_book = :id_book", {"id_book": id_book}).fetchone()
            revi = db.execute("SELECT rev_username, review, rating FROM reviews WHERE rev_book_id = :rev_book_id", {"rev_book_id": id_book}).fetchall()
            key = os.getenv("GOODREADS_KEY")
            res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": key, "isbns": bookdetail.isbn}).json()
            return render_template("review.html", bookdetail = bookdetail, res=res['books'][0], us=rev_username, message=message, revi=revi)
        bookdetail = db.execute("SELECT * FROM books WHERE id_book = :id_book", {"id_book": id_book}).fetchone()
        revi = db.execute("SELECT rev_username, review, rating FROM reviews WHERE rev_book_id = :rev_book_id", {"rev_book_id": id_book}).fetchall()
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "EKV1ySYo9Wbugb1ZQGbA", "isbns": bookdetail.isbn}).json()
        message = "SORRY! YOU ALREADY REVIEWED ON THIS BOOK!"
        return render_template("review.html", bookdetail = bookdetail, res=res['books'][0], us=rev_username, message=message, revi=revi)


@app.route("/api/<string:isbn>")
def api(isbn):
    if session.get('logged_in') != True:
       return abort(403)
    else:
        book_API = db.execute("SELECT isbn, title, author, year FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
        count_review = db.execute("SELECT count(review), avg(rating) FROM books JOIN reviews r ON id_book = r.rev_book_id WHERE isbn= :isbn GROUP BY id_book",{"isbn" :isbn}).fetchone()
        if count_review==None:
            co_rev = 0
            avg_rat = None
        else:
            co_rev = count_review[0]

            avg_rat = float(count_review[1])
        if book_API != None:
            res = {
                "isbn" : book_API[0],
                "title" : book_API[1],
                "author" : book_API[2],
                "yaer" : book_API[3],
                "review_count" : co_rev,
                "average_rating" : avg_rat
                }
            return json.dumps(res)
        return abort(404)
