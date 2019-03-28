# -*- coding: UTF-8 -*-
import os
from ast import literal_eval
from base64 import encodebytes
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from salt import salt_generator, key_salt_generator, decode_data
from smtp import enviarEmail
from datetime import datetime

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

salt_list = {}
dados_conexao = None

def get_salt(key):
    if key == None:
        return None
    gsalt = salt_list.get(key)
    if gsalt == None:
        return None
    if float(gsalt['validate']) < datetime.now().timestamp():
        salt_list.pop(key)
        return None
    else:
        return gsalt

def salve_salt_on_list(salt, host):
    now = datetime.now()
    key = key_salt_generator(host, now)
    salt_list[key] = salt
    return key

def validate_salt(salt):
    if salt == None:
        response = {'erro' : 'Salt inválido ou expirado', \
                    'mensagem' : 'O salt obtido com o Key-Salt informado não existe ou é inválido. \
                    Por favor gere outro Salt realizando um GET em \'/salt\''}
        return response
    else:
        return True

def validate_smtp_connection(smtp_conexao, salt_value):
    if smtp_conexao == None:
        response = {'erro' : 'Aussência dos dados de conexão', \
                    'mensagem' : 'Não foi possível identificar os dados de conexão. \
                    Por favor, informe os dados através do Header \'Data-Connection\'.'}
        return response
    smtp_conexao = decode_data(smtp_conexao, salt_value)
    try:
        smtp_conexao = literal_eval(smtp_conexao)
    except:
        response = {'erro' : 'Formatação inválida dos dados de conexão', \
                    'mensagem' : 'Não foi possível ler o JSON com os dados de conexão, \
                    a formatação parece estar incorreta.'}
        return response
    return (True, smtp_conexao)

@app.route("/salt", methods=['GET', 'PUT'])
@cross_origin()
def gsalt():
    if request.method == 'GET':
        gsalt = salt_generator()       
        response = jsonify(gsalt)
        host = request.headers['Host']
        response.headers['Key-Salt'] = salve_salt_on_list(gsalt, host)
        print(salt_list)
        response.headers['Access-Control-Expose-Headers'] = 'Key-Salt'
        return response
    elif request.method == 'PUT':
        key = request.get_json().get('key-salt')
        return jsonify(get_salt(key))

@app.route("/")
@cross_origin()
def hello():
    return None

@app.route("/send-email", methods=['PUT'])
@cross_origin()
def sendEmail():
    email = request.get_json().get('email')
    key_salt = request.headers.get('Key-Salt')
    salt = get_salt(key_salt)
    salt_valid = validate_salt(salt)
    if salt_valid != True:
        return jsonify(salt_valid)
    conexao_smtp = request.headers.get('Smtp-Connection')
    conexao_smtp_valid = validate_smtp_connection(conexao_smtp, salt['value'])
    if conexao_smtp_valid[0] != True:
            return jsonify(conexao_smtp_valid[1])
    response = enviarEmail(conexao_smtp_valid[1], email)
    return jsonify(response)
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)