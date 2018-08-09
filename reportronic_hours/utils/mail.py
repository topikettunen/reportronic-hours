import json
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText

class Mail:
    def __init__(self):
        absolute_path = os.path.abspath(os.path.dirname(__file__))
        config_path = os.path.join(absolute_path, "../config/config-test.json")
        with open(config_path) as config:
            data = json.load(config)
        self.mail_user = data['mail']['mail_user']
        self.password = data['mail']['password']
        self.mail_to = data['mail']['mail_to']

    def mail_body(self):
        msg = MIMEText('Hello, World')
        msg['Subject'] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S Reportronic Hours Output")
        msg['From'] = self.mail_user
        msg['To'] = self.mail_to
        return msg

    def send_mail(self):
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(self.mail_user, self.password)
        msg = self.mail_body()
        server.sendmail(self.mail_user, self.mail_to, msg.as_string())
