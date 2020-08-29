# Project 1

CS50-Web Programming with Python and JavaScript

# set ENV Variables
$ set FLASK_APP = application.py # flask run
$ set DATABASE_URL = Heroku Postgres DB URI
$ set GOODREADS_KEY = Goodreads API Key. # More info: https://www.goodreads.com/api

# Usage
* Register/login/logout
* Search books by name, author or ISBN
* Search Result shows n no. of books.
* Get info about a book from database as well as https://www.goodreads.com vie API
* submit your own review!

# About Project
* When the Application get starts, its will first check for the session (if you are already login), if session is present in cookies; it will redirect to search page either to login page.
* login page check for credentials, and redirect to search page only if credentials are correct, either give message as "USERNAME or PASSWORD incorrect".
* login page also contains the URL for registration page, similarly vice versa.
* Once, the user login, the user found his username on search page vie session username (i.e. Hi! <username>).
* user can search for book vie ISBN, Author or Title of the Book. result will show as per the query matched from search.
* Search Result shows n no. of books with information of ISBN, TITLE, AUTHOR and Button for more information.
* if user clicks on More info button, he/she found information through database(i.e. ISBN, author, title) and API of https://www.goodreads.com (i.e. Average ratings, total no. of ratings).
* user can also able to check the reviews from this site and can be able to give his/her own review at once for each book.
* finally user can able to get API of this website through "/api/<isbn>" only if the user is login either he/she gets error 403.
* logout button can destroy the session and redirect to login page.    
