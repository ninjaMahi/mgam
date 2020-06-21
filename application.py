import os
from datetime import datetime
from flask_session.__init__ import Session
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd
from cs50 import SQL


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
app.jinja_env.filters["usd"] = usd

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
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    portfolio_data=db.execute("SELECT Symbol,Name,SUM(Shares) FROM history WHERE id = :user GROUP BY Symbol",user=session["user_id"])

    portfolio = []
    final_total = 0
    

    cash = db.execute("SELECT cash FROM users WHERE id = :user",user=session["user_id"])
    cash = cash[0]['cash']
    cash=round(cash,2)

    for row in portfolio_data:
        stock_info2 = lookup(row['Symbol'])

        total = round(stock_info2['price']*row['SUM(Shares)'],2)
        final_total += total
        
        portfolio.append((stock_info2['symbol'], stock_info2['name'], row['SUM(Shares)'],stock_info2['price'],total))

    final_total=round(final_total+cash ,2)

   
    
    return render_template("index.html", portfolio=portfolio,final_total=final_total,cash=cash)



@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":



        shares = request.form.get("shares")
        stock = lookup(request.form.get("symbol"))
        symbol=stock['symbol']
        name=stock['name']


        if not lookup(symbol):
            return apology("Could not find the stock")

        price=stock['price']

        cash = db.execute("SELECT cash FROM users WHERE id = :user",user=session["user_id"])
        cash = cash[0]['cash']


        new_cash = round(cash - price * float(shares),2)


        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        db.execute("INSERT INTO history(id,Symbol,Name,Shares,Price,Total,Transacted) VALUES (:user,:symbol, :name, :shares,:price,:total,:transacted)",
                user=session["user_id"], symbol=symbol,name=name, shares=shares,price=price,total=price*float(shares),transacted=dt_string)

        db.execute("UPDATE users SET cash = :cash WHERE id = :user",
                          cash=new_cash, user=session["user_id"])

        flash("Bought!")
        return redirect("/")



    
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    rows = db.execute("SELECT * FROM history WHERE id = :user ORDER BY Transacted DESC",
                          user=session["user_id"])
    cash = db.execute("SELECT cash FROM users WHERE id = :user",
                          user=session["user_id"])
    cash = cash[0]['cash']
    
    transactions = []



    for row in rows:
        stock_info = lookup(row['Symbol'])


        # create a list with all the info about the transaction and append it to a list of every stock transaction
        transactions.append(list((stock_info['symbol'], stock_info['name'], row['Shares'], row['Price'],row['Price'] * float(row['Shares']),row['Transacted'])))

    
    print(transactions)
    return render_template("history.html", transactions=transactions)



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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":

        stock = lookup(request.form.get("symbol"))

        if not stock:
            return apology("Could not find the stock")

        return render_template("quoted.html", stock=stock)
    else:
        return render_template("quote.html", stock="")



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




@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":



        shares = request.form.get("sell_shares")
        stock = lookup(request.form.get("sell_symbol"))
        symbol=stock['symbol']
        name=stock['name']
        live_price=stock['price']


        if not lookup(symbol):
            return apology("Could not find the stock")



        cash = db.execute("SELECT cash FROM users WHERE id = :user",user=session["user_id"])
        cash = cash[0]['cash']

        portfolio = db.execute("SELECT Symbol FROM history WHERE id = :user",user=session["user_id"])
        stocks_owned=[]

        for i in portfolio:

            stocks_owned.append(i)

        new_cash = cash + live_price * float(shares)

        if not portfolio:

            return apology("Oops,Looks like you do not own the stock!")



        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        db.execute("INSERT INTO history(id,Symbol,Name,Shares,Price,Total,Transacted) VALUES (:user,:symbol, :name, :shares,:price,:total,:transacted)",
                user=session["user_id"], symbol=symbol,name=name, shares= -int(shares),price=live_price,total=live_price*float(shares),transacted=dt_string)

        db.execute("UPDATE users SET cash = :cash WHERE id = :user",
                          cash=new_cash, user=session["user_id"])
        flash("Sold!")

        return redirect("/")



    
    else:
        return render_template("sell.html")

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
