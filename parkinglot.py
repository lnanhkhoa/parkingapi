import datetime
import json,os

from flask import Flask, jsonify, request
from pymongo import MongoClient, ReturnDocument
from bson.json_util import dumps

app = Flask(__name__)

err = "0"
success = "1"
# Username password
# idparking01 123

post = {
    "author": "Mike",
    "text": "My first blog post!",
    "tags": ["mongodb", "python", "pymongo"],
    "date": datetime.datetime.utcnow()
}

client = MongoClient("mongodb://idparking01:123@ds047095.mlab.com:47095/userparkingpc")

db = client["userparkingpc"]
#db.create_collection("usersparkinglot")
users = db["usersparkinglot"]
status = db["status_parking"]
@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/api/insert_one/<username>', methods=["GET"])
def insert_one(username):
    checkExist = users.find({"username": username}).count()
    if checkExist > 0:
        return err
    else:
        user = {
            "username": username,
            "password": 123
        }
        collection.insert_one(user)
        return success

@app.route('/api/checkuser/<username>', methods=["GET"])
def checkuser(username):
    user = users.find_one({"username":username})
    if user is None:
        return err
    return success

@app.route('/api/update_status/<username>/<password>/<info>',methods=['GET'])
def update_status(username, password, info):
    #info = "12,300,10,100"
    info = info.split(',')
    for x in range (0,len(info)):
        info[x] = int(info[x])
    print info
    user = users.find_one({"username":username, "password":123})
    if user is None:
        return err
    updateStatus = status.find_one_and_update(  {"username":username},
                                                {'$set':{
                                                    "payload":{
                                                        "bike":info[0],"totalBike":info[1],"car":info[2],"totalCar":info[3]}
                                                    }
                                                },
                                                projection = {'username':True},
                                                upsert=True,
                                                return_document=ReturnDocument.AFTER)
    if updateStatus is None:
        return err
    return success

@app.route('/api/getinfomation',methods=['GET','POST'])
def get_infomation():
	statusAll = status.find(projection = {'payload':1,'username':1,'_id':0})
	return jsonify(result = json.loads(dumps(statusAll)))

port = os.getenv('PORT', '5000')
host = '0.0.0.0'
	
if __name__ == '__main__':
    app.run(host=host, port=int(port),debug=True,threaded=True)
