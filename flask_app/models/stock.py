from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app.models import user

class Stock:
    db_name = "stocks"
    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.symbol = data["symbol"]
        self.comments = data["comments"]
        self.P_E = data["P_E"]
        self.buy_hold_sell = None
        self.EV_to_EBITDA = data["EV_to_EBITDA"] 
        self.EV_to_Revenue = data["EV_to_Revenue"] 
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]
        self.selector = None

    @classmethod 
    def add_image(cls, data):
            query = """
            INSERT INTO favorites (date, explanation, image)
            VALUES (%(date)s, %(explanation)s, %(image)s)
            """
            return connectToMySQL(cls.db_name).query_db(query, data)

    @classmethod 
    def search_db_by_date(cls, data):
            query = """
                    SELECT * from favorites
                    WHERE DATE = (%(date)s)
                    """
            results = connectToMySQL(cls.db_name).query_db(query, data)
            print("Results:", results)
            if len(results) == 0:
                return None
            else:
                return cls(results[0])

    @classmethod
    def get_all_stocks(cls):
        query = """
        SELECT * FROM stocks
        Join users
        ON users.id = stocks.selector_id
        """
        results = connectToMySQL(cls.db_name).query_db(query)
        print("RESULTS:", results)
        list_of_stock_objects = []
        for this_stock_dictionary in results: 
    #Now we create the stock object:
            new_stock_object = cls(this_stock_dictionary)

    #Grab the selector's information:
            user_dictionary = {
                "id":this_stock_dictionary["users.id"],
                "first_name":this_stock_dictionary["first_name"],
                "last_name":this_stock_dictionary["last_name"],
                "email":this_stock_dictionary["email"],
                "password":this_stock_dictionary["password"],
                "created_at":this_stock_dictionary["users.created_at"],
                "updated_at":this_stock_dictionary["users.updated_at"]
            }
    #Create the user object:
            user_object = user.User(user_dictionary)

    #Link the user (creator) to this stock:
            new_stock_object.selector = user_object

            list_of_stock_objects.append(new_stock_object)
    
    #add the following code  in case there aren't any stocks in the database:

        if len(results) == 0:
            return []

        return list_of_stock_objects

    @classmethod
    def get_one_stock(cls, id):
        query = """
        SELECT * FROM stocks
        JOIN users
        ON users.id=stocks.selector_id
        WHERE stocks.id = %(id)s
        """
        data = {"id":id}
    #Below, need a data dictionary as we need the id of the stock.
        results = connectToMySQL(cls.db_name).query_db(query, data)
        print(results)
    #we use "results[0]", because SQL brings back a list of dictionaries. Here, we have one recipe dictionary that SQL brings back, so we use index of zero.
        if not results:
            return None
        else:
            new_stock_object = cls(results[0])
            print("new stock object:", new_stock_object)
            #Grab the selector's information:
            
            user_dictionary = {
                "id":results[0]["users.id"],
                "first_name":results[0]["first_name"],
                "last_name":results[0]["last_name"],
                "email":results[0]["email"],
                "password":results[0]["password"],
                "created_at":results[0]["users.created_at"],
                "updated_at":results[0]["users.updated_at"]
            }
    #Create the user object:
            user_object = user.User(user_dictionary)

    #Link the user (creator) to this recipe:
            new_stock_object.creator = user_object

#Results is a list, but we need to pass in a DICTIONARY, sp we need a specific dictionary, at this case at index 0. 
        return new_stock_object

    @classmethod
    def create_stock(cls, data_dictionary):
        query = """
        INSERT INTO stocks (symbol, name, comments, P_E, EV_to_EBITDA, EV_to_Revenue, selector_id) 
        VALUES (%(symbol)s, %(name)s, %(comments)s,  %(P_E)s, %(EV_to_EBITDA)s, %(EV_to_Revenue)s, %(selector_id)s)
        """
        return connectToMySQL(cls.db_name).query_db(query, data_dictionary)

    @classmethod
    def update_stock(cls, data_dictionary):
        query = """UPDATE stocks 
        SET comments = %(comments)s
        WHERE id = %(id)s
        """
        return connectToMySQL(cls.db_name).query_db(query, data_dictionary)

    
    @staticmethod 
    def validate_stocks(form_data):
        is_valid = True
        print (form_data)
        if len(form_data["comments"]) < 3:
            is_valid = False
            flash("Comments must be 3 more characters")
        
        return is_valid 
    
    @classmethod
    def delete_stock(cls,id):
        data = {"id":id}
        query = "DELETE FROM stocks where id = %(id)s"
        return connectToMySQL(cls.db_name).query_db(query, data)
    

        




