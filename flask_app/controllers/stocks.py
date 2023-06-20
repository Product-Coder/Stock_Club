import requests
from flask_app import app
import os
from flask import render_template, redirect, request, session, jsonify
from flask_app.models import stock, user
from pprint import pprint

@app.route('/search_process', methods=["POST"])
def search_API_Process():
    api_link = (f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={request.form['symbol']}&apikey={os.environ.get('alphavantage_API_KEY')}")

    response_string = requests.get(api_link)
    raw_data = response_string.json()
    print(raw_data)
    print(type(raw_data))

    session["Symbol"] = raw_data["Symbol"]
    session["Name"] = raw_data["Name"]
    session["Forward_PE"] = raw_data["ForwardPE"]
    session["EV_to_EBITDA"] = raw_data["EVToEBITDA"]
    session["EV_to_Revenue"] = raw_data["EVToRevenue"] 

    return redirect ("/search_results")

@app.route('/search_view')
def search_view():
    return render_template ("stock_search.html")

@app.route('/search_results')
def search_results():
    return render_template ("search_results.html")

@app.route('/stocks_table')         
def stocks_table(): 
    if "user_id" not in session:
        return redirect ('/register_&_login_view')
    else:
        All_stock_objects = stock.Stock.get_all_stocks()
        logged_user = user.User.grab_one_user_by_id({"id":session["user_id"]})
        return render_template ("stocks_table.html", logged_user=logged_user, List_Stock_Objects=All_stock_objects) 

@app.route('/stocks/view/<int:id>') #viewing one recipe          
def view_one_stock(id): 
    print("stock id",id)
    if "user_id" not in session:
        print ("not logged in, going back to root route")
        return redirect('/register_&_login_view')

    this_stock = stock.Stock.get_one_stock(id)
    print("this stock instance from SQL:", this_stock)
    logged_user = user.User.grab_one_user_by_id({"id":session["user_id"]})
    return render_template("view_stock.html", this_stock = this_stock, logged_user=logged_user)


@app.route('/add_stock_view')         
def add_stock_view():
    if "user_id" not in session:
        return redirect ('/register_&_login_view') 
    return render_template ("Add_Stock.html")

@app.route('/add_stock_process', methods = ["POST"])          
def add_stock_process():
    if "user_id" not in session:
        return redirect ('/register_&_login_view') 
    
    if not stock.Stock.validate_stocks(request.form):
        return redirect ("/add_stock_view")

    #Validae comments
    #use API to search for stock symbol entered by user and if it does not exist, need an erro message.

    api_link = (f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={request.form['symbol']}&apikey={os.environ.get('alphavantage_API_KEY')}")

   
    response_string = requests.get(api_link)
    raw_data = response_string.json()
    print("Raw data for added stock:", raw_data)

    Forward_PE = raw_data["ForwardPE"]
    EV_to_EBITDA = raw_data["EVToEBITDA"]
    EV_to_Revenue = raw_data["EVToRevenue"] 

    #if validations are good, take the three columns from the API, and save them as variables.
    #then can put the variables in the dictionary.

    this_stock_results = {
        "symbol":request.form["symbol"],
        "name":request.form["name"],
        "comments":request.form["comments"],
        "P_E": Forward_PE,
        "EV_to_EBITDA": EV_to_EBITDA,
        "EV_to_Revenue": EV_to_Revenue,
        "selector_id": session["user_id"]#This links the logged in user to the stock we are selecting.
    }
    stock.Stock.create_stock(this_stock_results)
    # session.modified = True # To allow the list to change
    # session["added_companies"].append(form_results)
#Above, Session does not save data if you are using a mutbale (something that changes after a function is done) object like a list or dictionary. To allow saving dictionaries and lsits in session, need to add the code "session.modified = True" (row 67)
    return redirect ("/stocks_table")

@app.route('/stocks/edit/<int:id>') #viewing one recipe          
def edit_stock(id):
    this_stock = stock.Stock.get_one_stock(id)
    return render_template("edit_stock.html", this_stock = this_stock)

@app.route('/stocks/edit_process/<int:id>', methods = ["POST"]) #viewing one recipe          
def edit_stock_process(id):
    if "user_id" not in session:
        print ("not logged in, going back to root route")
        return redirect('/register_&_login_view')
    if not stock.Stock.validate_stocks(request.form):
        return redirect (f"/stocks/edit/{id}")
    form_results = {
            "comments":request.form["comments"],
            "id":id #so we know which query to edit in the database
        }
    print("These are the form_results for comments", request.form["comments"])
    stock.Stock.update_stock(form_results)

    return redirect('/stocks_table')

@app.route('/stocks/delete/<int:id>')           
def delete_stock(id):
    if "user_id" not in session:
        print ("not logged in, going back to root route")
        return redirect('/register_&_login_view')
    stock.Stock.delete_stock(id)
    return redirect ('/stocks_table')

       
   
 

