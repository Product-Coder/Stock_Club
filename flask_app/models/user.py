from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash #for validation messages, which will appear  after selecting submit.The moment we clcik somewhere else or click or refresh, the message dissapears, which is why it's called flash.
from flask_app import app
from flask_bcrypt import Bcrypt 
bcrypt = Bcrypt(app)
import re #Regex, for email validation
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

class User:
    db_name = "stocks" #We are adding a class variable, so we don't have to repeat the schema names in each class method below.
    def __init__(self, data_dictionary): #data_dictionary is a dictionary from your database
        self.id = data_dictionary["id"]
        self.first_name = data_dictionary["first_name"]
        self.last_name = data_dictionary["last_name"]
        self.email = data_dictionary["email"]
        self.password = data_dictionary["password"]
        self.created_at = data_dictionary["created_at"]
        self.updated_at = data_dictionary["updated_at"]
        self.stocks = [] # Place holder for holding MANY recipes
    
    #validating registration

    @classmethod 
    def register_user(cls, data):
        query = """
        INSERT INTO users (first_name, last_name, email, password)
        VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s)
        """
        return connectToMySQL(cls.db_name).query_db(query, data)

        #Above will return the user id, which is useful so we can save the ID in session and then not let a user in if they are not properly registered.

    @classmethod
    def grab_one_user_by_id(cls, data):
        query =  "SELECT * FROM users WHERE id = %(id)s" 
        results = connectToMySQL(cls.db_name).query_db(query, data)
        # print("These are the results:" + results)
        #Let's add logic for the edge case that we don't find anyone with the given ID:
        if len(results) == 0:
            return None 
        else:
            print("these are the results for the user ID that is registered:", results)
            return cls(results[0]) #Create a user object from the results list at index 0.
        #Results is a list of dictionaries. In this case, it will return just one user, so we pull results[0]. 
        #Next, we will grab this user in users,py "def dashboard():"

    @classmethod
    def grab_one_user_by_email(cls, data):
        query =  "SELECT * FROM users WHERE email = %(email)s" 
        results = connectToMySQL(cls.db_name).query_db(query, data)
        print("I am here")
        print(results)
        if len(results) < 1: #if we don't find an email, we will return none
            return None 
        else:
            return cls(results[0])


    @staticmethod
    def validate_registration(form_data):
        is_valid = True #we are assuming everything looks good
        #The momement any validation fails, the boolean variable is set to False ("is_valid")

        #first name is a string and you can use "len" method to tell you how many characters are in a string.
        if len(form_data["first_name"]) < 3:
            flash("First name must be at least 3 characters.", "registration")
            is_valid = False
        if len(form_data["last_name"]) < 3:
            flash("Last name must be at least 3 characters.", "registration")
            is_valid = False
        if not EMAIL_REGEX.match(form_data['email']): 
            flash("Invalid email address!", "registration")
            is_valid = False
        if form_data["password"] != form_data["confirm_password"]:
            flash("Password field needs to match Confirm Password field", "registration")
            is_valid = False
        if len(form_data["password"]) < 8:
            flash("Password must be at least eight characters.", "registration")
            is_valid = False

        #Check to see if someone already registered with that email.
        #Grab someone with that email if possible.
        #Just like we grabbed a user by id in "grab_one_user_by_id(cls, data)", we are going to do the same thing but grab one user by email (just added this in lines 47-53). We cannot grab anything from a class method or instance variables in a static method. So, we have to call on user class from within the user class.

        #withing the below method, we need to pass in a dictionary with the email. the "form_data" is passed through from "request.form" in "def register():" in the model , user.py file.
        Found_User_Or_None = User.grab_one_user_by_email({"email":form_data["email"]}) 
        print ("Found_User_Or_None:", Found_User_Or_None)
        #Line 87 shows that if a user email is not found, None is returned
        if Found_User_Or_None != None:
            flash("user already registered with that email.", "registration")
            is_valid = False
        print("is_valid=", is_valid)
        return is_valid 

    @staticmethod
    def validate_login(form_data):
        is_valid = True
        #try to findsomeone with that email
        Found_User_Or_None = User.grab_one_user_by_email({"email":form_data["email"]}) 
        if Found_User_Or_None == None: #There's no need to check the password.
            flash("Invalid login credentials", "login") #Do not givr a specific error message like invalid email or invalid password. This could let a hacker know that they got the correct email but just need to hack into the password or vice versa. We don't want hackers to know whether the email or the password was wrong or both.
            is_valid = False
            return False #no need to check password if no user found, so add return statement to stop validation.
            #If someone exists with this email, then check the password.
        if not bcrypt.check_password_hash(Found_User_Or_None.password, form_data["password"]): #Found_User_Or_None returns an object (see grab_one_user_by_email method, where it makes an object) if the emails match. Then, we look at the object and see if the email entered in the loggin form matches the password in the object (which include the correct password for the given email address). 
            #Above,Found_User_Or_None is the object of the user that registered. We want to see if the password you entered in the form to register 
                flash("Invalid login credentials", "login")
                is_valid = False
        return is_valid
                





    
