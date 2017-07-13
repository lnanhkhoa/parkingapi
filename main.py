# coding=utf-8
import os
from api import app

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

port = os.getenv('PORT', '5000')
host = '127.0.0.1'

if __name__ == '__main__':
    app.run(host=host, port=int(port), debug=True)