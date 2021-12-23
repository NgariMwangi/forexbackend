from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import requests,json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_cors import CORS

app = Flask(__name__)
alvapi_key = "4198SX701V7XO9UP"
scheduler = BackgroundScheduler(daemon=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
cors = CORS(app, resources={r"*": {"origins": "*"}})


class Forex(db.Model):
    __name__="forex"
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(80), nullable=False)
    data = db.Column(db.JSON, unique=True)
    created_date  = db.Column(db.DateTime, nullable=False, server_default=func.now())

    
@app.before_first_request
def create_db():
    db.create_all()


@app.route("/")
def index():
   return "This is a private API"

@app.route("/json/forex")
def forex_api():
    #Get from DB
    data_json=Forex.query.all()
    import ast
    res =json.dumps([ast.literal_eval(d.data) for d in data_json])
    return res
    
 
def request_scheduler():
    # try:
        # Make a GET Request to Alphavantage
        r = requests.get('https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol=IBM&apikey=' + alvapi_key)
        #Store the data received
        data = r.text
        #Find out type of data
        print(type(data))
        #Convert from string
        data_json = json.loads(data)
        #Find out type of data
        print("From scheduler:",type(data_json))

        data = Forex(symbol="IBM", data=json.dumps(data_json))
        db.session.add(data)
        db.session.commit()
    # except Exception as e:
    #     print("Error in scheduler:")


#Create the scheduler job
scheduler.add_job(request_scheduler, 'interval', minutes=0.25)
#start the scheduler
scheduler.start()

    

if __name__ == "__main__":
    app.run()