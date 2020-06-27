import os
from datetime import datetime
from flask_session.__init__ import Session
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required
from cs50 import SQL
import random

#test1
# Configure application
app = Flask(__name__)

#app.secret_key = "12345"

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "23456"
Session(app)

SECRET_KEY = 'fZIL19uN68Y6wD2C76kTTQ'

if not SECRET_KEY:
    raise ValueError("No SECRET_KEY set for Flask application")


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///m-games.db")

@app.route("/")
@login_required
def index():
    
    
    return render_template("index.html")

@app.route("/hangman_single",methods=["GET", "POST"])
@login_required
def hangman_single():
    
    if request.method == "GET":

        db.execute("DELETE FROM hangman WHERE id =:id",id=session["user_id"])



        #declaring variables 

        file = open("words.txt", "r")
        line_list = list()
        for line in file:
            line_list.append(line.rstrip('\n'))
        user_guess_list=list()

        randomline = line_list[random.randint(1, 200)]
        letter_list = list(randomline)
        user_letters_list=[" "," "," "," "," "," "]
        db.execute("INSERT INTO hangman(id,word) VALUES (:id,:word)",
            id=session["user_id"],word=str(randomline))

        return render_template("hangman_single.html",user_letters_list=user_letters_list)


    else:

        word=db.execute("SELECT word FROM hangman WHERE id=:id",id=session["user_id"])
        print(word)
        word =word[0]['word']
        user_letters_list=db.execute("SELECT first,second,third,fourth,fifth,sixth FROM hangman WHERE id=:id",id=session["user_id"])
        user_letters_list=[user_letters_list[0]['first'],user_letters_list[0]['second'],user_letters_list[0]['third'],user_letters_list[0]['fourth'],user_letters_list[0]['fifth'],user_letters_list[0]['sixth']]
        lives=db.execute("SELECT lives FROM hangman WHERE id=:id",id=session["user_id"])[0]['lives']
        total_letters=db.execute("SELECT total_letters FROM hangman WHERE id=:id",id=session["user_id"])[0]['total_letters']
        print("total_letters : " +str(total_letters))
        user_letter_guess=request.form.get("user_guess")


        hearts="💙"*lives
        print(lives)
        print(hearts)
        if user_letter_guess==word[0]:
            db.execute("UPDATE hangman SET first = :letter,total_letters= :total WHERE id = :user_id", letter=user_letter_guess,total=total_letters+1,user_id = session["user_id"])
            total_letters+=1
        if user_letter_guess==word[1]:
            db.execute("UPDATE hangman SET second = :letter,total_letters= :total WHERE id = :user_id", letter=user_letter_guess,total=total_letters+1,user_id = session["user_id"])
            total_letters+=1
        if user_letter_guess==word[2]:
            db.execute("UPDATE hangman SET third = :letter,total_letters= :total WHERE id = :user_id", letter=user_letter_guess,total=total_letters+1,user_id = session["user_id"])
            total_letters+=1
        if user_letter_guess==word[3]:
            db.execute("UPDATE hangman SET fourth = :letter,total_letters= :total WHERE id = :user_id", letter=user_letter_guess,total=total_letters+1,user_id = session["user_id"])
            total_letters+=1

        if user_letter_guess==word[4]:
            db.execute("UPDATE hangman SET fifth = :letter,total_letters= :total WHERE id = :user_id", letter=user_letter_guess,total=total_letters+1,user_id = session["user_id"])
            total_letters+=1

        if user_letter_guess==word[5]:
            db.execute("UPDATE hangman SET sixth = :letter,total_letters= :total WHERE id = :user_id", letter=user_letter_guess,total=total_letters+1,user_id = session["user_id"])
            total_letters+=1
        elif user_letter_guess!=word[0] and user_letter_guess!=word[1] and user_letter_guess!=word[2] and user_letter_guess!=word[3] and user_letter_guess!=word[4] and user_letter_guess!=word[5]:
            lives-=1
            if lives==0:
                db.execute("DELETE FROM hangman WHERE id =:id",id=session["user_id"])
                return render_template("game_over.html",word=word)
            db.execute("UPDATE hangman SET lives = :lives WHERE id = :user_id", lives=lives,user_id = session["user_id"])
            hearts="💙"*lives
            print(lives)
            print(hearts)
        
        if total_letters==6:
            db.execute("DELETE FROM hangman WHERE id =:id",id=session["user_id"])
            return render_template("game_complete.html",word=word)



        user_letters_list=db.execute("SELECT first,second,third,fourth,fifth,sixth FROM hangman WHERE id=:id",id=session["user_id"])
        user_letters_list=[user_letters_list[0]['first'],user_letters_list[0]['second'],user_letters_list[0]['third'],user_letters_list[0]['fourth'],user_letters_list[0]['fifth'],user_letters_list[0]['sixth']]

        return render_template("hangman_single.html",user_letters_list=user_letters_list,hearts=hearts)

@app.route("/hangman_multi_word",methods=["GET", "POST"])
@login_required
def hangman_multi_word():
    if request.method == "GET":

        db.execute("DELETE FROM hangman WHERE id =:id",id=session["user_id"])
        return render_template("hangman_multi_word.html")
    
    else:
 
        letter_list = list(request.form.get("user_word"))
        user_letters_list=[" "," "," "," "," "," "]
        db.execute("INSERT INTO hangman(id,word) VALUES (:id,:word)",
            id=session["user_id"],word=request.form.get("user_word"))

        return render_template("hangman_multi.html",user_letters_list=user_letters_list)


@app.route("/hangman_multi",methods=["GET", "POST"])
@login_required
def hangman_multi():
    
    if request.method == "GET":

        return render_template("hangman_multi.html",user_letters_list=[" "," "," "," "," "," "])


    else:

        word=db.execute("SELECT word FROM hangman WHERE id=:id",id=session["user_id"])
        word =word[0]['word']
        print(word)
        user_letters_list=db.execute("SELECT first,second,third,fourth,fifth,sixth FROM hangman WHERE id=:id",id=session["user_id"])
        user_letters_list=[user_letters_list[0]['first'],user_letters_list[0]['second'],user_letters_list[0]['third'],user_letters_list[0]['fourth'],user_letters_list[0]['fifth'],user_letters_list[0]['sixth']]
        lives=db.execute("SELECT lives FROM hangman WHERE id=:id",id=session["user_id"])[0]['lives']
        user_letter_guess=request.form.get("user_guess")
        total_letters=db.execute("SELECT total_letters FROM hangman WHERE id=:id",id=session["user_id"])[0]['total_letters']
        print("total_letters : " +str(total_letters))

        hearts="💙"*lives
        print(lives)
        print(hearts)
        if user_letter_guess==word[0]:
            db.execute("UPDATE hangman SET first = :letter,total_letters= :total WHERE id = :user_id", letter=user_letter_guess,total=total_letters+1,user_id = session["user_id"])
            total_letters+=1
        if user_letter_guess==word[1]:
            db.execute("UPDATE hangman SET second = :letter,total_letters= :total WHERE id = :user_id", letter=user_letter_guess,total=total_letters+1,user_id = session["user_id"])
            total_letters+=1
        if user_letter_guess==word[2]:
            db.execute("UPDATE hangman SET third = :letter,total_letters= :total WHERE id = :user_id", letter=user_letter_guess,total=total_letters+1,user_id = session["user_id"])
            total_letters+=1
        if user_letter_guess==word[3]:
            db.execute("UPDATE hangman SET fourth = :letter,total_letters= :total WHERE id = :user_id", letter=user_letter_guess,total=total_letters+1,user_id = session["user_id"])
            total_letters+=1

        if user_letter_guess==word[4]:
            db.execute("UPDATE hangman SET fifth = :letter,total_letters= :total WHERE id = :user_id", letter=user_letter_guess,total=total_letters+1,user_id = session["user_id"])
            total_letters+=1

        if user_letter_guess==word[5]:
            db.execute("UPDATE hangman SET sixth = :letter,total_letters= :total WHERE id = :user_id", letter=user_letter_guess,total=total_letters+1,user_id = session["user_id"])
            total_letters+=1
        elif user_letter_guess!=word[0] and user_letter_guess!=word[1] and user_letter_guess!=word[2] and user_letter_guess!=word[3] and user_letter_guess!=word[4] and user_letter_guess!=word[5]:
            lives-=1
            if lives==0:
                return render_template("game_over.html",word=word)
            db.execute("UPDATE hangman SET lives = :lives WHERE id = :user_id", lives=lives,user_id = session["user_id"])
            hearts="💙"*lives
            print(lives)
            print(hearts)


        if total_letters==6:
            db.execute("DELETE FROM hangman WHERE id =:id",id=session["user_id"])
            return render_template("game_complete.html",word=word)

        user_letters_list=db.execute("SELECT first,second,third,fourth,fifth,sixth FROM hangman WHERE id=:id",id=session["user_id"])
        user_letters_list=[user_letters_list[0]['first'],user_letters_list[0]['second'],user_letters_list[0]['third'],user_letters_list[0]['fourth'],user_letters_list[0]['fifth'],user_letters_list[0]['sixth']]

        return render_template("hangman_multi.html",user_letters_list=user_letters_list,hearts=hearts)

@app.route("/hangman",methods=["GET", "POST"])
@login_required
def hangman():
    
    if request.method == "GET":
        return render_template("hangman_game_choice.html")
        
    else:
        if request.form.get('hangman_choice') == 'normal':
            return redirect("/hangman_single")
        elif request.form.get('hangman_choice') == 'multi':
            return redirect("/hangman_multi_word")

    
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    
    
    if request.method == "GET":
        return render_template("login.html")

    else:
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        print("rows : "+str(rows))
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")




@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        elif not request.form.get("re-password"):
            return apology("must provide password twice", 403)

        elif request.form.get("password")!=request.form.get("re-password"):
            return apology("passwords do not match", 403)

        elif db.execute("SELECT * FROM users WHERE username = :username",
            username=request.form.get("username")):
            return apology("Username already taken", 403)


        # Query database for username
        db.execute("INSERT INTO users(username, hash) VALUES (:username, :hash)",
            username=request.form.get("username"), hash=generate_password_hash(request.form.get("password")))

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
            username=request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")



@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change password"""

    if request.method == "POST":

        if not request.form.get("old_password"):
            return apology("must provide old password", 403)

        # Ensure password was submitted
        elif not request.form.get("new_password"):
            return apology("must provide new_password", 403)

        elif not request.form.get("new_re-password"):
            return apology("must provide new pasword twice", 403)

        elif request.form.get("new_re-password")!=request.form.get("new_password") :
            return apology("passwords do not match", 403)


        
        rows = db.execute("SELECT * FROM users WHERE id = :user_id",
                          user_id= session["user_id"])
        real_password=rows[0]["hash"]
        old_password=request.form.get("old_password")
        print("real_password "+real_password)
        print("old_password "+old_password)
        
        
        
        if not check_password_hash(real_password,old_password):
            return apology("old passwords is invalid", 403)
        
        
        
        new_password=generate_password_hash(request.form.get("new_password"))

        db.execute("UPDATE users SET hash = :hash WHERE id = :user_id", hash=new_password,user_id = session["user_id"])

        
        return redirect("/")






    else:
        return render_template("change_password.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
