import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64

# create a base_url so we do not keep repeating links that have the same base
base_url = 'https://sandbox.safaricom.co.ke/'

# copy the consumer key provided when you create an app in Daraja
consumer_key = 'AGKNfcSVoU0uyZ8dIVtfBsHeWsngW6WA'

# copy the consumer secret provided when you create an app in Daraja
consumer_secret = 'OpQsvcNlJVmuHGxH'

# the business short code is the one provided in the Lipa Na M-Pesa Online API section of the documentation (https://developer.safaricom.co.ke/Documentation#:~:text=%C2%A0%22BusinessShortCode%22%3A%22174379%22%2C%C2%A0%20%C2%A0)
business_short_code = "174379"

passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'

def authenticator():
    r = requests.get(base_url+'oauth/v1/generate?grant_type=client_credentials', auth=HTTPBasicAuth(consumer_key, consumer_secret))

    # since r.json() returns a dictionary (something like ), we use the access_token key to get the token
    return r.json()['access_token']

def get_timestamp():
    # use the datetime library to get the current time
    sai = datetime.now()

    # format the string to look like the one provided in the Lipa Na M-Pesa Online API section of the documentation here: https://developer.safaricom.co.ke/Documentation#:~:text=%22Timestamp%22%3A%2220160216165627%22%2C%C2%A0%20%C2%A0%C2%A0
    sai_string = sai.strftime("%Y%m%d%H%M%S")
    
    return sai_string

def generate_password():
    # this is the password used for encrypting the request sent: A base64 encoded string. The base4 encoded string is a combination of Shortcode + Passkey + Timestamp
    # from the documentation, the password that we are going to encrypt is a combination of the business shortcode, the passkey, and the current timestamp
    password_to_encrypt = business_short_code + passkey + get_timestamp()

    # we then encode the password using base64
    encrypted_password = base64.b64encode(password_to_encrypt.encode())

    # we then decode the password to get the actual password
    decoded_password = encrypted_password.decode('utf-8')

    return decoded_password



authenticator()
get_timestamp()
generate_password()

