import string
import random
from base64 import b64encode, b64decode
from datetime import datetime, timedelta

def salt_validate_generator():
    now = datetime.now()
    delta = timedelta(hours=1)
    validate = now + delta
    return str(validate.timestamp())

def salt_generator(size=21, chars=string.ascii_uppercase + string.digits):
    salt = {}
    salt['value'] = ''.join(random.choice(chars) for _ in range(size))
    salt['validate'] = salt_validate_generator()
    return salt

def key_salt_generator(host, date):
    key = salt_generator().get('value') + '$' +  host  + '$' + str(date.timestamp())
    key = b64encode(str(key).encode('utf-8')).decode('utf-8')
    return key

def decode_data(data, salt):
    data_decoded = b64decode(str(data).encode('utf-8')).decode('utf-8')
    return str(data_decoded).replace(salt, '')