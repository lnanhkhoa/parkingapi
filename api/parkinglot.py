# coding=utf-8

import datetime
import json
import random
import string

from bson.json_util import dumps
from pymongo import MongoClient, ReturnDocument, collection

from flask import jsonify, request
from api import app
from flask_mail import Message, Mail
from apiMail import MailConfirm, MailForgot


err = 0
success = 1
not_authenticated = 2
existed = 3


mail = Mail(app)
app.config.update(
    DEBUG=True,
    # EMAIL SETTINGS
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_TLS=False,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='iot.smartparking@gmail.com',
    MAIL_PASSWORD='matkhaulagi'
)


def password_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def sentmail(recipients, content):
    try:
        message = content
        subject = "hello, %s" % recipients
        msg = Message(recipients=[recipients],
                      sender="iot.smartparking@gmail.com",
                      body=message,
                      subject=subject)
        mail.send(msg)
        return success
    except:
        return err

# Username password
# idparking01 123

post = {
    "author": "Mike",
    "text": "My first blog post!",
    "tags": ["mongodb", "python", "pymongo"],
    "date": datetime.datetime.utcnow()
}

client = MongoClient("mongodb://parkingAPI:parkingapi.heroku@ds047095.mlab.com:47095/userparkingpc")

db = client["userparkingpc"]
# db.create_collection("usersparkinglot")

users = db["usersparkinglot"]
status = db["status_parking"]
userInApp = db["usersInApp"]


@app.route("/authentication/<username>/<id>", methods=['GET','POST'])
def authentication(username, id):
    userAuthen = userInApp.find_one({"username": username})
    if userAuthen is not None:
        if userAuthen['is_authenticated']:
            return jsonify(results=success)
        oid = str(userAuthen['_id'])
        if id == oid:
            userupdate = userInApp.update_one({"username": username},
                                              {'$set': {"is_authenticated": True}})
            if userupdate.acknowledged:
                return jsonify(results=success)
    return jsonify(results=err)


@app.route('/checkaccount/<username>/<password>', methods=['GET','POST'])
def login(username, password):
    if request.method == 'GET':
        userAuthen = userInApp.find_one({"username": username, "password": password})
        if userAuthen is not None:
            if userAuthen["is_authenticated"] is True:
                return jsonify(results=success)
            else:
                return jsonify(results=not_authenticated)
    return jsonify(results=err)


@app.route("/register/<email>/<username>/<password>", methods=['GET','POST'])
def register(email, username, password):
    if request.method == 'GET':
        checkExist = userInApp.find({"username": username}).count()
        if checkExist > 0:
            return jsonify(results=existed)
        else:
            user = {
                "username": username,
                "email": email,
                "password": password,
                "is_authenticated": False
            }
            result_one = userInApp.insert_one(user)
            id = str(result_one.inserted_id)
            content = MailConfirm.replace("$domain$", str(request.url_root)).replace("$authen$",
                                                                                     str(username + "/" + id))
            result_sent = sentmail(email, content)
            if result_sent == success:
                return jsonify(results=success)
    return jsonify(results=err)


@app.route("/changepassword/<username>/<oldpass>/<newpass>", methods=['GET','POST'])
def changepassword(username, oldpass, newpass):
    userAuthen = userInApp.find_one({"username": username, "password": oldpass})
    if userAuthen is not None:
        if userAuthen["is_authenticated"] is False:
            return jsonify(results=not_authenticated)
        userupdate = userInApp.update_one({"username": username, "password": oldpass},
                                          {'$set': {"password": newpass}}
                                          )
        if userupdate.acknowledged:
            return jsonify(results=success)
            # return jsonify(results = json.loads(dumps(userupdate)))
    return jsonify(results=err)


@app.route("/forgotpassword/<email>", methods=['GET','POST'])
def forgotpassword(email):
    user = userInApp.find_one({"email": email})
    if user is not None:
        if user["is_authenticated"] is False:
            return jsonify(results=not_authenticated)
        username = user['username']
        newpass = password_generator()
        result_one = userInApp.update_one({"email": email},
                                          {'$set': {"password": newpass}})
        content = MailForgot.replace("$email$", email).replace("$username$", username).replace("$password$", newpass)
        result_sent = sentmail(email, content)
        if result_sent == "Sent":
            return jsonify(results=success)
    return jsonify(results=err)


#########################################################################################


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/api/insert_one/<username>', methods=["GET"])
def insert_one(username):
    checkExist = users.find({"username": username}).count()
    if checkExist > 0:
        jsonify(results=err)
    else:
        user = {
            "username": username,
            "password": 123
        }
        # collection.insert_one(user)
        jsonify(results=success)


@app.route('/api/checkuser/<username>', methods=["GET"])
def checkuser(username):
    user = users.find_one({"username": username})
    if user is None:
        return err
    return success


@app.route('/api/update_status/<username>/<password>/<info>', methods=['GET'])
def update_status(username, password, info):
    # info = "12,300,10,100"
    info = info.split(',')
    for x in range(0, len(info)):
        info[x] = int(info[x])
    user = users.find_one({"username": username, "password": 123})
    if user is None:
        return err
    updateStatus = status.find_one_and_update({"username": username},
                                              {'$set': {
                                                  "payload": {
                                                      "bike": info[0], "totalBike": info[1], "car": info[2],
                                                      "totalCar": info[3]}
                                              }
                                              },
                                              projection={'username': True},
                                              upsert=True,
                                              return_document=ReturnDocument.AFTER)
    if updateStatus is None:
        return err
    return success


@app.route('/api/getinformation', methods=['POST'])
def get_information():
    if request.method == 'POST':
        statusAll = status.find(projection={'payload': 1, 'username': 1, '_id': 0})
        return jsonify(results=json.loads(dumps(statusAll)))
    return jsonify(results=err)
