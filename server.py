from flask_app import app
#import controllers:
from flask_app.controllers import stocks, users

if __name__=="__main__":   
    app.run(debug=True)    # Run the app in debug mode.