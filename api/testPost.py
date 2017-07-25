

import requests

data = {
    "username":"lnanhkhoa",
    "password":"1234",
    "bike":0,
    "totalBike":100,
    "car":0,
    "totalCar":300

}

data1 = {
    "username":"lnanhkhoa",
    "password":"1234",
    "Longitude":"10.848406",
    "Latitude":"106.774707",
    "Address":"Coop Mart, Nga 4 Thu Duc, Tp. HCM"
}
r = requests.post('http://127.0.0.1:5000/api/update_status', data = data)
# r = requests.post('http://127.0.0.1:5000/api/insert_one', data = data1)


print r.text