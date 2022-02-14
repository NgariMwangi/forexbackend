

from flask import Flask, render_template,request,jsonify,make_response
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import requests,json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_cors import CORS
from mpesa import *

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



class STKData(db.Model):
    __tablename__ = 'stkdata'

    id = db.Column(db.Integer, primary_key=True)
    merchant_request_id = db.Column(db.String(80), nullable=False)
    checkout_request_id = db.Column(db.String(80), nullable=False)
    response_code = db.Column(db.String(80), nullable=False)
    response_description = db.Column(db.String(80), nullable=False)
    customer_message = db.Column(db.String(80), nullable=False)
    created_date = db.Column(db.DateTime, nullable=False, server_default=func.now())

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
@app.route('/signup',methods=["POST","GET"])
def sign():
    if request.method=="POST":
       print("fhwf kwe ")

@app.route("/stkpush", methods=["POST"])
def stk_push():
    data=request.get_json(force=True)
    print("jkjbbb",data["phone"])
    phone_number = data["phone"]
    account_number = '25747'
    amount = 1
    header = {'Authorization': 'Bearer %s' % authenticator()}
    url = base_url + 'mpesa/stkpush/v1/processrequest'
    body = {
        "BusinessShortCode": business_short_code,
        "Password": generate_password(),
        "Timestamp": get_timestamp(),
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": business_short_code,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://ec96-41-80-150-214.ngrok.io/stkpush/checker",
        "AccountReference": account_number,
        "TransactionDesc": "Edwin is shouting at us"
    }
    r=requests.post(url, json=body, headers=header).json()

    print(r)
    stored_response_data = STKData(merchant_request_id = r['MerchantRequestID'], checkout_request_id = r['CheckoutRequestID'], response_code = r['ResponseCode'], response_description = r['ResponseDescription'], customer_message = r['CustomerMessage'])
    db.session.add(stored_response_data)
    db.session.commit()



    return r



@app.route("/stkpush/checker", methods=["POST","GET"])
def stk_checker():
   # 2. Change the status code received in step 1
    safaricom_data = request.get_json(force=True)
    print(safaricom_data)
    print(type(safaricom_data))
    updated=STKData.query.filter_by(checkout_request_id = safaricom_data['Body']['stkCallback']['CheckoutRequestID'], merchant_request_id = safaricom_data['Body']['stkCallback']['MerchantRequestID']).update({STKData.response_code:safaricom_data['Body']['stkCallback']['ResultCode'], STKData.response_description:safaricom_data['Body']['stkCallback']['ResultDesc']})
    db.session.commit()

   
    return safaricom_data 

@app.route("/stkpush/processor", methods=['GET', 'POST'])
def stk_push_processor():
    # 3. Check what the user has done. The client shall do a loop every 5 seconds with the checkout request and the merchant request.
    print(':::::::::  ENTERING PROCESSOR :::::::::')
    apiData = request.get_json(force=True)
    print(apiData)
    processorQueriedRecord = STKData.query.filter_by(checkout_request_id = apiData['checkout'], merchant_request_id = apiData['merchant']).first()
    if processorQueriedRecord:
        # resp = make_resonse(jsonify(dict({'':processorQueriedRecord.mid, '':processorQueriedRecord.cr, })),200()
        resp =  jsonify(dict({'MerchantRequestID':processorQueriedRecord.merchant_request_id, 'ResultDesc':processorQueriedRecord.response_description, 'ResponseCode':processorQueriedRecord.response_code}))
        print('this is resp',resp)       
        resp = make_response(resp,200)
        print(resp)
        return resp
       
    else:
        return {'error':'error'}
   


    

        
    

    
    
def request_scheduler():

    # try:
    #     # Make a GET Request to Alphavantage
    #     r = requests.get('https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol=IBM&apikey=' + alvapi_key)
    #     #Store the data received
    #     data = r.text
    #     #Find out type of data
    #     print(type(data))
    #     #Convert from string
    #     data_json = json.loads(data)
    #     #Find out type of data
    #     print("From scheduler:",type(data_json))

    #     data = Forex(symbol="IBM", data=json.dumps(data_json))
    #     db.session.add(data)
    #     db.session.commit()
    # except Exception as e:
        # print("Error in scheduler:")
    return "hi"


#Create the scheduler job
scheduler.add_job(request_scheduler, 'interval', minutes=0.25)
#start the scheduler
scheduler.start()

    

if __name__ == "__main__":
    app.run()