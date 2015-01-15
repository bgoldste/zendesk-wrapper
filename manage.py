from flask.ext.script import Manager
from flask import Flask

import zendesk

import os
from postmark import PMMail

app = Flask(__name__)
print app

manager = Manager(app)

@manager.command
def hello():
	# zendesk do stuff
	# if need to send message, then do it
	if zendesk.main():
		message = PMMail(api_key = "621fc6db-f9a7-44c8-90f3-e294803465ed",
		                 subject = "Yo, Zendesk is not Gucci!",
		                 sender = "ben@kimonolabs.com",
		                 to = "yeezus@kimonolabs.com",
		                 text_body = "Hello, You're getting this email because there are currently more than 10 tickets in zendesk. Can you hop on and check it out rl quick? Thanks!",
		                 tag = "hello")

		message.send()
	else:
		print 
		"not printing"

if __name__ == "__main__":
  manager.run()